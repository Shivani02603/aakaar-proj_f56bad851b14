import { ReactNode } from 'react';
import AuthGuard from '@/components/AuthGuard';

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <AuthGuard>
      <div className="bg-white min-h-screen">
        <main className="container mx-auto px-4 py-6">{children}</main>
      </div>
    </AuthGuard>
  );
}