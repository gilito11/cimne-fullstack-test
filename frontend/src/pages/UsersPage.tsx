import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "../api/client";
import type { Role, User } from "../api/types";
import { useAuth } from "../auth/AuthContext";

async function fetchUsers(): Promise<User[]> {
  const r = await api.get<User[]>("/users");
  return r.data;
}

export function UsersPage() {
  const { user: me } = useAuth();
  const qc = useQueryClient();
  const { data, isLoading, error } = useQuery({ queryKey: ["users"], queryFn: fetchUsers });
  const [editing, setEditing] = useState<string | null>(null);
  const [editUsername, setEditUsername] = useState("");
  const [editRole, setEditRole] = useState<Role>("user");

  const updateMut = useMutation({
    mutationFn: (vars: { id: string; username: string; role: Role }) =>
      api.put<User>(`/users/${vars.id}`, { username: vars.username, role: vars.role }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["users"] });
      setEditing(null);
    },
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => api.delete(`/users/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["users"] }),
  });

  if (isLoading) return <div className="container">Loading users…</div>;
  if (error) return <div className="container error">Could not load users.</div>;

  const isAdmin = me?.role === "admin";

  return (
    <div className="container">
      <div className="card">
        <h1>Users</h1>
        <p className="muted">
          {isAdmin
            ? "You can edit any user and delete users."
            : "You can only edit your own profile. Admins can manage all users."}
        </p>
        <table>
          <thead>
            <tr>
              <th>Username</th>
              <th>Email</th>
              <th>Role</th>
              <th style={{ textAlign: "right" }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {data?.map((u) => {
              const canEdit = isAdmin || me?.id === u.id;
              const isEditing = editing === u.id;
              return (
                <tr key={u.id}>
                  <td>
                    {isEditing ? (
                      <input
                        value={editUsername}
                        onChange={(e) => setEditUsername(e.target.value)}
                      />
                    ) : (
                      u.username
                    )}
                  </td>
                  <td>{u.email}</td>
                  <td>
                    {isEditing && isAdmin ? (
                      <select value={editRole} onChange={(e) => setEditRole(e.target.value as Role)}>
                        <option value="user">user</option>
                        <option value="admin">admin</option>
                      </select>
                    ) : (
                      u.role
                    )}
                  </td>
                  <td style={{ textAlign: "right" }}>
                    {isEditing ? (
                      <>
                        <button
                          className="primary"
                          style={{ marginRight: 6, padding: "0.35rem 0.7rem" }}
                          onClick={() =>
                            updateMut.mutate({ id: u.id, username: editUsername, role: editRole })
                          }
                          disabled={updateMut.isPending}
                        >
                          Save
                        </button>
                        <button className="danger" onClick={() => setEditing(null)}>
                          Cancel
                        </button>
                      </>
                    ) : (
                      <>
                        {canEdit && (
                          <button
                            className="danger"
                            style={{ marginRight: 6 }}
                            onClick={() => {
                              setEditing(u.id);
                              setEditUsername(u.username);
                              setEditRole(u.role);
                            }}
                          >
                            Edit
                          </button>
                        )}
                        {isAdmin && me?.id !== u.id && (
                          <button
                            className="danger"
                            onClick={() => {
                              if (confirm(`Delete user ${u.username}?`)) deleteMut.mutate(u.id);
                            }}
                            disabled={deleteMut.isPending}
                          >
                            Delete
                          </button>
                        )}
                      </>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
