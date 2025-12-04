# Bank Statement Frontend

Modern, fintech-focused frontend for the Bank Statement Management System built with Next.js 14, TypeScript, and Tailwind CSS.

## Features

- 🔐 Authentication (Login/Register)
- 📊 Dashboard with financial overview
- 💰 Transaction management
- 📈 Financial reports
- 💱 Currency conversion
- 📤 CSV file upload
- 🎨 Modern, responsive UI

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Environment Variables

Create a `.env.local` file:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Project Structure

```
frontend/
├── app/                    # Next.js app directory
│   ├── dashboard/         # Dashboard pages
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Home/login page
├── components/            # React components
│   ├── LoginPage.tsx
│   ├── Sidebar.tsx
│   ├── TransactionList.tsx
│   └── ...
├── contexts/              # React contexts
│   └── AuthContext.tsx
├── lib/                   # Utilities
│   └── api.ts            # API client
└── public/               # Static assets
```

## API Integration

The frontend connects to the Django REST API backend. Make sure the backend is running on `http://localhost:8000` (or update `NEXT_PUBLIC_API_URL`).

## Build for Production

```bash
npm run build
npm start
```

## Technologies

- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **React Hook Form** - Form management
- **Lucide React** - Icons
- **Recharts** - Charts (for reports)

