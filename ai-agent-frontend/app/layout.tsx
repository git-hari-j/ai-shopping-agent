export const metadata = {
  title: 'AI Shopping Assistant',
  description: 'Futuristic shopping experience',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-slate-900 text-slate-100 min-h-screen flex flex-col">
        {children}
      </body>
    </html>
  )
}
