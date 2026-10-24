import StationMap from "./components/StationMap.jsx";
import sampleStations from "./data/sampleStations.json";

function App() {
  return <StationMap stations={sampleStations} />;
}

export default App;
