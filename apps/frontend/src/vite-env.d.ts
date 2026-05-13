/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_VOICE_MODE?: "push_to_talk" | "continuous";
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
