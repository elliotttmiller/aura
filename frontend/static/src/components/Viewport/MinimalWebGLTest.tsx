import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';

export default function MinimalWebGLTest() {
  return (
    <div className="minimal-webgl-test-root">
      <Canvas
        className="minimal-webgl-test-canvas"
        dpr={1}
        gl={{ antialias: false, preserveDrawingBuffer: false }}
        onCreated={({ gl }) => {
          gl.domElement.addEventListener('webglcontextlost', (e) => {
            e.preventDefault();
            alert('WebGL context lost! (Minimal Test)');
          });
        }}
      >
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} />
        <mesh rotation={[0.4, 0.2, 0]}>
          <boxGeometry args={[2, 2, 2]} />
          <meshStandardMaterial color={'orange'} />
        </mesh>
        <OrbitControls />
      </Canvas>
    </div>
  );
}
