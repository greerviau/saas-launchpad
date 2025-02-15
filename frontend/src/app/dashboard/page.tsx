import Navbar from "@/components/navbar";
import ProtectedRoute from "@/components/protected-route";

export default function Dashboard() {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="p-6">
          <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Dashboard cards */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-lg font-semibold mb-2">Quick Stats</h2>
              <p className="text-gray-600">Your dashboard content here</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-lg font-semibold mb-2">Recent Activity</h2>
              <p className="text-gray-600">Activity feed goes here</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-lg font-semibold mb-2">Tasks</h2>
              <p className="text-gray-600">Your tasks list here</p>
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
