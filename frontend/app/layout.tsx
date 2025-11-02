import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'OfficeLightNavi - 施設照明ナビ',
  description: '施設照明器具の選定を支援する対話型エージェント',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  )
}

