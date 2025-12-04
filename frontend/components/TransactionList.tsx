import { format } from "date-fns";
import { ArrowUpRight, ArrowDownRight } from "lucide-react";

interface Transaction {
  id: number;
  date: string;
  amount: number;
  currency: string;
  converted_amount?: number;
  converted_currency?: string;
  description: string;
  type: "credit" | "debit";
  category: string;
}

interface TransactionListProps {
  transactions: Transaction[];
}

export default function TransactionList({ transactions }: TransactionListProps) {
  if (transactions.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p>İşlem bulunamadı</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-gray-200">
            <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Tarih</th>
            <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Açıklama</th>
            <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Kategori</th>
            <th className="text-right py-3 px-4 text-sm font-medium text-gray-700">Tutar</th>
            <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Tür</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((transaction) => (
            <tr key={transaction.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
              <td className="py-3 px-4 text-sm text-gray-900">
                {format(new Date(transaction.date), "MMM dd, yyyy")}
              </td>
              <td className="py-3 px-4 text-sm text-gray-900">{transaction.description}</td>
              <td className="py-3 px-4">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                  {transaction.category || "Kategorisiz"}
                </span>
              </td>
              <td className="py-3 px-4 text-right">
                <div className="flex items-center justify-end gap-2">
                  {transaction.converted_amount !== undefined && transaction.converted_currency ? (
                    <>
                      <span className={`text-sm font-semibold ${
                        transaction.type === "credit" ? "text-success-600" : "text-danger-600"
                      }`}>
                        {transaction.type === "credit" ? "+" : "-"}
                        {transaction.converted_amount.toLocaleString(undefined, {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        })}
                      </span>
                      <span className="text-xs text-gray-500">{transaction.converted_currency}</span>
                      <span className="text-xs text-gray-400">
                        ({transaction.amount} {transaction.currency})
                      </span>
                    </>
                  ) : (
                    <span className={`text-sm font-semibold ${
                      transaction.type === "credit" ? "text-success-600" : "text-danger-600"
                    }`}>
                      {transaction.type === "credit" ? "+" : "-"}
                      {transaction.amount.toLocaleString(undefined, {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })}
                    </span>
                  )}
                </div>
              </td>
              <td className="py-3 px-4">
                <div className="flex items-center gap-2">
                  {transaction.type === "credit" ? (
                    <ArrowUpRight className="w-4 h-4 text-success-600" />
                  ) : (
                    <ArrowDownRight className="w-4 h-4 text-danger-600" />
                  )}
                  <span className="text-sm text-gray-600">{transaction.type === "credit" ? "Gelir" : "Gider"}</span>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

