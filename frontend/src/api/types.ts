export type Role = "admin" | "user";

export interface User {
  id: string;
  username: string;
  email: string;
  role: Role;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface BuildingIndicator {
  reference: string;
  name?: string | null;
  indicator: string;
  value?: number | null;
  lat?: number | null;
  lng?: number | null;
  calculation_date?: string | null;
}
