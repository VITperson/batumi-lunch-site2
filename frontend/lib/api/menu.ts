import axios from 'axios';
import type { MenuWeek } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000/api/v1';

export async function fetchMenuWeek(): Promise<MenuWeek> {
  const response = await axios.get<MenuWeek>(`${API_BASE}/menu/week`);
  return response.data;
}
