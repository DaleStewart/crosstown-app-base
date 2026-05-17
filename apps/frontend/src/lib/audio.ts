export type PcmCallback = (pcm: ArrayBuffer) => void;

export interface MicSession {
  stop(): Promise<void>;
}

export async function startMic(onPcm: PcmCallback): Promise<MicSession> {
  const stream = await navigator.mediaDevices.getUserMedia({
    audio: { channelCount: 1, echoCancellation: true, noiseSuppression: true },
  });
  // AudioContext is created after an async gap so browsers (Chrome autoplay
  // policy) may start it suspended. Wrap setup in try/catch so we always
  // release the mic stream if anything here fails.
  let ctx: AudioContext | null = null;
  try {
    ctx = new AudioContext();
    await ctx.resume();
    const source = ctx.createMediaStreamSource(stream);
    const processor = ctx.createScriptProcessor(4096, 1, 1);
    const targetRate = 16000;

    processor.onaudioprocess = (ev: AudioProcessingEvent) => {
      const input = ev.inputBuffer.getChannelData(0);
      const ratio = (ctx as AudioContext).sampleRate / targetRate;
      const outLen = Math.floor(input.length / ratio);
      const out = new Int16Array(outLen);
      for (let i = 0; i < outLen; i++) {
        const sample = input[Math.floor(i * ratio)] ?? 0;
        const clipped = Math.max(-1, Math.min(1, sample));
        out[i] = clipped < 0 ? clipped * 0x8000 : clipped * 0x7fff;
      }
      onPcm(out.buffer);
    };

    source.connect(processor);
    processor.connect((ctx as AudioContext).destination);

    const capturedCtx = ctx;
    return {
      async stop(): Promise<void> {
        processor.disconnect();
        source.disconnect();
        stream.getTracks().forEach((t) => t.stop());
        await capturedCtx.close();
      },
    };
  } catch (err) {
    // Ensure the mic indicator light goes off even if Web Audio setup fails.
    stream.getTracks().forEach((t) => t.stop());
    if (ctx) await ctx.close().catch(() => undefined);
    throw err;
  }
}

export class AudioPlayer {
  private ctx: AudioContext | null = null;
  private nextStartTime = 0;

  ensure(): AudioContext {
    if (!this.ctx) this.ctx = new AudioContext();
    return this.ctx;
  }

  enqueuePcm16(base64: string, sampleRate = 24000): void {
    const ctx = this.ensure();
    const bytes = base64ToBytes(base64);
    if (bytes.byteLength === 0) return;
    const samples = new Int16Array(bytes.buffer, bytes.byteOffset, bytes.byteLength / 2);
    const floatBuf = ctx.createBuffer(1, samples.length, sampleRate);
    const ch = floatBuf.getChannelData(0);
    for (let i = 0; i < samples.length; i++) {
      ch[i] = (samples[i] ?? 0) / 0x8000;
    }
    const src = ctx.createBufferSource();
    src.buffer = floatBuf;
    src.connect(ctx.destination);
    const start = Math.max(ctx.currentTime, this.nextStartTime);
    src.start(start);
    this.nextStartTime = start + floatBuf.duration;
  }

  async pause(): Promise<void> {
    if (this.ctx) await this.ctx.suspend();
  }

  async resume(): Promise<void> {
    if (this.ctx) await this.ctx.resume();
  }
}

function base64ToBytes(b64: string): Uint8Array {
  const bin = atob(b64);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}
