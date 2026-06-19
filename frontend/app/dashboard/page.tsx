```tsx
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { getToken } from '@/lib/auth';
import { listSessions } from '@/api/client';
import { CreateSessionResponse } from '@/api/client';

interface StatCardProps {
  title: string;
  value: number;
  description: string;
}

const StatCard = ({ title, value, description }: StatCardProps) => (
  <div className="bg-white shadow-md rounded-lg p-4">
    <h3 className="text-lg font-semibold">{title}</h3>
    <p className="text-2xl font-bold mt-2">{value}</p>
    <p className="text-sm text-gray-500 mt-1">{description}</p>
  </div>
);

interface RecentItem {
  id: string;
  title: string;
  createdAt: string;
}

const DashboardPage = () => {
  const [sessions, setSessions] = useState<CreateSessionResponse[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchSessions = async () => {
      setLoading(true);
      setError(null);

      try {
        const token = getToken();
        if (!token) {
          router.push('/login');
          return;
        }

        const response = await listSessions(token);
        setSessions(response);
      } catch (err) {
        setError('Failed to fetch sessions. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchSessions();
  }, [router]);

  const recentItems: RecentItem[] = sessions
    .slice(0, 5)
    .map((session) => ({
      id: session.id,
      title: session.title,
      createdAt: session.createdAt,
    }));

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <StatCard
          title="Sessions"
          value={sessions.length}
          description="Total number of sessions created."
        />
        <StatCard
          title="AI Queries"
          value={0} // Placeholder, replace with actual data when available
          description="Total number of AI queries processed."
        />
        <StatCard
          title="Clients"
          value={0} // Placeholder, replace with actual data when available
          description="Total number of clients onboarded."
        />
      </div>

      <div className="bg-white shadow-md rounded-lg p-4">
        <h2 className="text-lg font-semibold mb-4">Recent Sessions</h2>
        {loading ? (
          <p className="text-gray-500">Loading...</p>
        ) : error ? (
          <p className="text-red-500">{error}</p>
        ) : recentItems.length === 0 ? (
          <p className="text-gray-500">No recent sessions found.</p>
        ) : (
          <table className="w-full border-collapse border border-gray-200">
            <thead>
              <tr className="bg-gray-100">
                <th className="border border-gray-200 px-4 py-2 text-left">Title</th>
                <th className="border border-gray-200 px-4 py-2 text-left">Created At</th>
              </tr>
            </thead>
            <tbody>
              {recentItems.map((item) => (
                <tr key={item.id}>
                  <td className="border border-gray-200 px-4 py-2">{item.title}</td>
                  <td className="border border-gray-200 px-4 py-2">
                    {new Date(item.createdAt).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
```