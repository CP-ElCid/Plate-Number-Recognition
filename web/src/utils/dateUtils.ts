/**
 * Format a date string or Date object to Philippine time
 * @param date - ISO string, Date object, or timestamp
 * @returns Formatted date string in Philippine time
 */
export function toPhilippineTime(date: string | Date): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;

  return dateObj.toLocaleString('en-PH', {
    timeZone: 'Asia/Manila',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true
  });
}

/**
 * Format a date to Philippine date only (no time)
 * @param date - ISO string, Date object, or timestamp
 * @returns Formatted date string in Philippine time (date only)
 */
export function toPhilippineDate(date: string | Date): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;

  return dateObj.toLocaleDateString('en-PH', {
    timeZone: 'Asia/Manila',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
}

/**
 * Format a date to Philippine time only (no date)
 * @param date - ISO string, Date object, or timestamp
 * @returns Formatted time string in Philippine time
 */
export function toPhilippineTimeOnly(date: string | Date): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;

  return dateObj.toLocaleTimeString('en-PH', {
    timeZone: 'Asia/Manila',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true
  });
}
