import uuid
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from database.db import get_connection

class ConversationManager:
    def create_conversation(self, title: str = "New Chat") -> Dict[str, Any]:
        conv_id = str(uuid.uuid4())
        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO conversations (id, title) VALUES (?, ?)",
                (conv_id, title)
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM conversations WHERE id = ?", (conv_id,)
            ).fetchone()
            return dict(row)
        finally:
            conn.close()

    def get_conversations(self) -> List[Dict[str, Any]]:
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM conversations ORDER BY updated_at DESC"
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def get_conversation(self, conv_id: str) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM conversations WHERE id = ?", (conv_id,)
            ).fetchone()
            if not row:
                return None
            conv = dict(row)
            messages = conn.execute(
                "SELECT * FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC",
                (conv_id,)
            ).fetchall()
            conv["messages"] = [dict(m) for m in messages]
            docs = conn.execute(
                "SELECT * FROM documents WHERE conversation_id = ? ORDER BY uploaded_at DESC",
                (conv_id,)
            ).fetchall()
            conv["documents"] = [dict(d) for d in docs]
            return conv
        finally:
            conn.close()

    def update_conversation(self, conv_id: str, title: str) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        try:
            conn.execute(
                "UPDATE conversations SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (title, conv_id)
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM conversations WHERE id = ?", (conv_id,)
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def delete_conversation(self, conv_id: str) -> bool:
        conn = get_connection()
        try:
            cursor = conn.execute(
                "DELETE FROM conversations WHERE id = ?", (conv_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def clear_all_conversations(self) -> int:
        conn = get_connection()
        try:
            cursor = conn.execute("DELETE FROM conversations")
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()

    def add_message(
        self, conv_id: str, role: str, content: str,
        message_type: str = "text", file_name: Optional[str] = None
    ) -> Dict[str, Any]:
        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO messages (conversation_id, role, content, message_type, file_name) VALUES (?, ?, ?, ?, ?)",
                (conv_id, role, content, message_type, file_name)
            )
            conn.execute(
                "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (conv_id,)
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM messages WHERE conversation_id = ? ORDER BY id DESC LIMIT 1",
                (conv_id,)
            ).fetchone()
            return dict(row)
        finally:
            conn.close()

    def get_messages(self, conv_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC LIMIT ?",
                (conv_id, limit)
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def get_conversation_history(self, conv_id: str, limit: int = 20) -> List[Dict[str, str]]:
        messages = self.get_messages(conv_id, limit)
        return [
            {"role": m["role"], "content": m["content"]}
            for m in messages
            if m["message_type"] == "text"
        ]

    def add_document(
        self, conv_id: str, doc_id: str, file_name: str,
        file_type: str, file_size: int, content_preview: str = "",
        page_count: int = 0
    ) -> Dict[str, Any]:
        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO documents (id, conversation_id, file_name, file_type, file_size, content_preview, page_count) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (doc_id, conv_id, file_name, file_type, file_size, content_preview, page_count)
            )
            conn.commit()
            row = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
            return dict(row)
        finally:
            conn.close()

    def save_fitness_data(self, data_type: str, data: Dict) -> Dict[str, Any]:
        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO fitness_data (data_type, data_json) VALUES (?, ?)",
                (data_type, json.dumps(data))
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM fitness_data ORDER BY id DESC LIMIT 1"
            ).fetchone()
            return dict(row)
        finally:
            conn.close()

    def get_fitness_data(self, data_type: str, limit: int = 30) -> List[Dict[str, Any]]:
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM fitness_data WHERE data_type = ? ORDER BY recorded_at DESC LIMIT ?",
                (data_type, limit)
            ).fetchall()
            result = []
            for r in rows:
                d = dict(r)
                d["data"] = json.loads(d["data_json"])
                del d["data_json"]
                result.append(d)
            return result
        finally:
            conn.close()

    def auto_title(self, conv_id: str, first_message: str) -> str:
        title = first_message[:50].strip()
        if len(first_message) > 50:
            title += "..."
        self.update_conversation(conv_id, title)
        return title

# Singleton
conversation_manager = ConversationManager()
