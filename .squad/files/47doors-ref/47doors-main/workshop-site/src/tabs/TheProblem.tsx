import CollapsibleNotes from '../components/CollapsibleNotes'
import CalloutCard from '../components/CalloutCard'
import DiagramSVG from '../components/DiagramSVG'

export default function TheProblem() {
  return (
    <div role="tabpanel" id="problem-panel" aria-labelledby="problem-tab">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-3xl font-semibold text-dark-text mb-8">
          Students Don't Know Which Door to Knock On
        </h2>

        <DiagramSVG 
          title="47 University Front Doors"
          description="Each icon represents a separate university portal or support system"
          viewBox="0 0 800 300"
        >
          {/* Grid of 47 door icons */}
          {Array.from({ length: 47 }).map((_, i) => {
            const row = Math.floor(i / 10)
            const col = i % 10
            const x = 50 + col * 70
            const y = 40 + row * 60
            
            return (
              <g key={i}>
                <rect 
                  x={x} 
                  y={y} 
                  width="50" 
                  height="40" 
                  fill="#F3F2F1" 
                  stroke="#323130" 
                  strokeWidth="2"
                  rx="4"
                />
                <rect 
                  x={x + 20} 
                  y={y + 15} 
                  width="10" 
                  height="20" 
                  fill="#0078D4"
                  rx="2"
                />
              </g>
            )
          })}
        </DiagramSVG>

        <div className="grid md:grid-cols-2 gap-8 my-12">
          <div className="card">
            <h3 className="font-semibold text-xl mb-4 text-dark-text">Before: Chaos</h3>
            <ul className="space-y-2 text-gray-700">
              <li>• IT Support portal</li>
              <li>• Financial Aid system</li>
              <li>• Housing portal</li>
              <li>• Dining services</li>
              <li>• Registrar office</li>
              <li>• Library help desk</li>
              <li>• Academic advising</li>
              <li>• Health services</li>
              <li>• Parking & transportation</li>
              <li>• Athletics support</li>
              <li>• Career services</li>
              <li>• ...and 36 more</li>
            </ul>
          </div>

          <div className="card bg-microsoft-blue/5">
            <h3 className="font-semibold text-xl mb-4 text-dark-text">After: One Door</h3>
            <div className="flex flex-col items-center justify-center h-full">
              <div className="text-6xl mb-4">🚪</div>
              <p className="text-lg font-medium text-center text-dark-text">
                47 Doors Agent
              </p>
              <p className="text-sm text-gray-600 text-center mt-2">
                Routes to the right department automatically
              </p>
            </div>
          </div>
        </div>

        <CalloutCard variant="accent" title="The Real Problem">
          The student doesn't have a routing problem. The university has a design problem.
        </CalloutCard>

        <div className="grid md:grid-cols-3 gap-6 mt-12">
          <div className="card text-center">
            <div className="text-3xl font-bold text-microsoft-blue mb-2">3.2</div>
            <p className="text-sm text-gray-600">
              Average departments contacted before reaching the right one
            </p>
          </div>

          <div className="card text-center">
            <div className="text-3xl font-bold text-microsoft-blue mb-2">67%</div>
            <p className="text-sm text-gray-600">
              Support tickets misrouted on first attempt
            </p>
          </div>

          <div className="card text-center">
            <div className="text-3xl font-bold text-microsoft-blue mb-2">30-50+</div>
            <p className="text-sm text-gray-600">
              Separate support portals at most universities
            </p>
          </div>
        </div>

        <CollapsibleNotes>
          <p className="mb-3">
            Imagine being a first-year student at a large university. You have a password problem — 
            but is that IT? Or is it your course portal? Maybe it's your library login?
          </p>
          <p className="mb-3">
            Students waste hours figuring out which door to knock on — and often knock on the wrong one. 
            This creates duplicate tickets, frustrated students, and overworked support staff who spend 
            their time routing tickets instead of solving problems.
          </p>
          <p>
            The 47 Doors project gives students ONE front door. Behind that door, an intelligent routing 
            system ensures they reach the right department on the first try — whether they type or talk.
          </p>
        </CollapsibleNotes>
      </div>
    </div>
  )
}
