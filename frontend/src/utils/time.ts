export const formatTime = (time: string) => {
  if (!time) return { date: "-", time: "-" };

  const utcTime = time.endsWith("Z") ? time : `${time}Z`;
  const date = new Date(utcTime);

  const formatted = date.toLocaleString("zh-CN", {
    timeZone: "Asia/Shanghai",
    hour12: false,
  });

  const [d, t] = formatted.split(" ");

  return {
    date: d.replace(/\//g, "-"),
    time: t,
  };
};