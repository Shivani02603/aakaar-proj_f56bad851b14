'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'react-toastify';
import { CreateMessageRequest, CreateMessageResponse, CreateSessionRequest, CreateSessionResponse, File, IngestRequest, LoginRequest, LoginResponse } from '@/api/client';
import { getToken } from '@/lib/auth';

interface AiItem {
  id: string;
  name: string;
  description: string;
  createdAt: string;
}

export default function AiPage() {
  const [aiItems, setAiItems] = useState<AiItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchAiItems = async () => {
      setLoading(true);
      setError(null);

      try {
        const token = getToken();
        const response = await fetch('/api/ai', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch AI items.');
        }

        const data: AiItem[] = await response.json();
        setAiItems(data);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    };

    fetchAiItems();
  }, []);

  const handleDelete = async (id: string) => {
    try {
      const token = getToken();
      const response = await fetch(`/api/ai/${id}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete AI item.');
      }

      setAiItems((prev) => prev.filter((item) => item.id !== id));
      toast.success('AI item deleted successfully.');
    } catch (err) {
      toast.error((err as Error).message);
    }
  };

  if (loading) {
    return <div className="text-center py-4">Loading...</div>;
  }

  if (error) {
    return <div className="text-center py-4 text-red-500">{error}</div>;
  }

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">AI Items</h1>
      <table className="table-auto w-full border-collapse border border-gray-300">
        <thead>
          <tr>
            <th className="border border-gray-300 px-4 py-2">ID</th>
            <th className="border border-gray-300 px-4 py-2">Name</th>
            <th className="border border-gray-300 px-4 py-2">Description</th>
            <th className="border border-gray-300 px-4 py-2">Created At</th>
            <th className="border border-gray-300 px-4 py-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          {aiItems.map((item) => (
            <tr key={item.id}>
              <td className="border border-gray-300 px-4 py-2">{item.id}</td>
              <td className="border border-gray-300 px-4 py-2">{item.name}</td>
              <td className="border border-gray-300 px-4 py-2">{item.description}</td>
              <td className="border border-gray-300 px-4 py-2">{item.createdAt}</td>
              <td className="border border-gray-300 px-4 py-2">
                <button
                  className="bg-red-500 text-white px-4 py-2 rounded"
                  onClick={() => handleDelete(item.id)}
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}