import { LuClock, LuLeaf, LuUsers } from "react-icons/lu";
import { useRouter } from "next/router";

export default function StatsCard({ totalObservations, speciesCount, shannonIndex }) {
  const router = useRouter();

  const stats = [
    {
      icon: LuClock,
      iconColor: "text-primary",
      label: "Totale osservazioni",
      value: totalObservations,
      borderColor: "border-primary",
    },
    {
      icon: LuLeaf,
      iconColor: "text-success",
      label: "Specie distinte",
      value: speciesCount,
      borderColor: "border-success",
      clickable: true,
      onClick: () => router.push("/species"),
    },
    {
      icon: LuUsers,
      iconColor: "text-warning",
      label: "Indice di Shannon",
      value: shannonIndex?.toFixed(3) ?? "N/A",
      borderColor: "border-warning",
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
      {stats.map((stat, index) => (
        <div
          key={index}
          className={`bg-white rounded-lg shadow-md p-5 border-l-4 ${stat.borderColor} ${stat.clickable ? "cursor-pointer hover:bg-gray-50 transition" : ""}`}
          onClick={stat.onClick}
        >
          <div className="flex items-center gap-2 mb-1">
            <stat.icon className={`${stat.iconColor} h-5 w-5`} />
            <span className="text-sm font-medium text-muted">{stat.label}</span>
          </div>
          <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
        </div>
      ))}
    </div>
  );
}