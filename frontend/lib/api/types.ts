export interface DayOffer {
  id: number;
  day_of_week: string;
  items: string[];
  calories?: number | null;
  allergy_tag_ids: number[];
  price_lari?: number | null;
  status: 'available' | 'sold_out' | 'closed';
  portion_limit?: number | null;
  sold_out: boolean;
  photo_url?: string | null;
}

export interface MenuWeek {
  id: number;
  week_start: string;
  title?: string | null;
  description?: string | null;
  is_published: boolean;
  order_deadline_hour: number;
  base_price_lari: number;
  day_offers: DayOffer[];
}
