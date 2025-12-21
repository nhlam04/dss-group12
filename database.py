
import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict
from charity_decision_system import (
    CharityAgent, GrantRequest, ProgramCategory, UrgencyLevel,
    AllocationDecision, FundAllocationResult
)


class Database:
    """Database"""
    
    def __init__(self, db_path: str = "charity_fund.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA journal_mode=WAL')
        return conn
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS charity_agents (
                agent_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                transparency_score REAL NOT NULL,
                total_programs_completed INTEGER NOT NULL DEFAULT 0,
                programs_succeeded INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grant_requests (
                request_id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER NOT NULL,
                program_name TEXT NOT NULL,
                amount_requested REAL NOT NULL,
                overhead_cost REAL NOT NULL,
                people_benefitted INTEGER NOT NULL,
                duration_months INTEGER NOT NULL,
                category TEXT NOT NULL,
                urgency TEXT NOT NULL,
                sustainability_score REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                succeeded INTEGER DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES charity_agents(agent_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fund_config (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                total_budget REAL NOT NULL,
                allocated_budget REAL DEFAULT 0,
                min_allocation_percentage REAL DEFAULT 0.5,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS allocation_history (
                allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT NOT NULL,
                total_budget REAL NOT NULL,
                total_allocated REAL NOT NULL,
                remaining_budget REAL NOT NULL,
                num_fully_funded INTEGER,
                num_partially_funded INTEGER,
                num_rejected INTEGER,
                total_people_benefitted INTEGER,
                average_efficiency REAL,
                allocation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS allocation_decisions (
                decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
                allocation_id INTEGER NOT NULL,
                request_id TEXT NOT NULL,
                amount_allocated REAL NOT NULL,
                allocation_percentage REAL NOT NULL,
                priority_score REAL NOT NULL,
                rank INTEGER NOT NULL,
                rationale TEXT,
                FOREIGN KEY (allocation_id) REFERENCES allocation_history(allocation_id),
                FOREIGN KEY (request_id) REFERENCES grant_requests(request_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS criteria_weights (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                people_benefitted REAL DEFAULT 0.25,
                efficiency REAL DEFAULT 0.20,
                success_rate REAL DEFAULT 0.15,
                cost_effectiveness REAL DEFAULT 0.15,
                urgency REAL DEFAULT 0.10,
                sustainability REAL DEFAULT 0.10,
                transparency REAL DEFAULT 0.05,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            INSERT OR IGNORE INTO fund_config (id, total_budget, allocated_budget)
            VALUES (1, 0, 0)
        """)

        cursor.execute("""
            INSERT OR IGNORE INTO criteria_weights (id) VALUES (1)
        """)
        
        conn.commit()
        conn.close()

    
    def add_agent(self, name: str, transparency_score: float, 
                  total_programs_completed: int = 0, programs_succeeded: int = 0) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO charity_agents 
                (name, transparency_score, total_programs_completed, programs_succeeded)
                VALUES (?, ?, ?, ?)
            """, (name, transparency_score, total_programs_completed, programs_succeeded))
            agent_id = cursor.lastrowid
            conn.commit()
            return agent_id
        finally:
            conn.close()
    
    def get_agent(self, agent_id: int) -> Optional[CharityAgent]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM charity_agents WHERE agent_id = ?", (agent_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return CharityAgent(
                agent_id=str(row['agent_id']),
                name=row['name'],
                transparency_score=row['transparency_score'],
                total_programs_completed=row['total_programs_completed'],
                programs_succeeded=row['programs_succeeded']
            )
        return None
    
    def get_all_agents(self) -> List[CharityAgent]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM charity_agents ORDER BY name")
        rows = cursor.fetchall()
        conn.close()
        
        agents = []
        for row in rows:
            agents.append(CharityAgent(
                agent_id=str(row['agent_id']),
                name=row['name'],
                transparency_score=row['transparency_score'],
                total_programs_completed=row['total_programs_completed'],
                programs_succeeded=row['programs_succeeded']
            ))
        return agents
    
    def update_agent(self, agent_id: int, name: str, transparency_score: float,
                     total_programs_completed: int, programs_succeeded: int) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE charity_agents 
            SET name = ?, transparency_score = ?,
                total_programs_completed = ?, programs_succeeded = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE agent_id = ?
        """, (name, transparency_score, total_programs_completed, 
              programs_succeeded, agent_id))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    
    def delete_agent(self, agent_id: int) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM charity_agents WHERE agent_id = ?", (agent_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    
    def add_request(self, agent_id: int, program_name: str, amount_requested: float,
                    overhead_cost: float, people_benefitted: int, duration_months: int,
                    category: str, urgency: str, sustainability_score: float) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO grant_requests 
                (agent_id, program_name, amount_requested, overhead_cost,
                 people_benefitted, duration_months, category, urgency,
                 sustainability_score, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
            """, (agent_id, program_name, amount_requested, overhead_cost,
                  people_benefitted, duration_months, category, urgency,
                  sustainability_score))
            request_id = cursor.lastrowid
            conn.commit()
            return request_id
        finally:
            conn.close()
    
    def get_request(self, request_id: int) -> Optional[GrantRequest]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM grant_requests WHERE request_id = ?", (request_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            agent = self.get_agent(row['agent_id'])
            if agent:
                return GrantRequest(
                    request_id=str(row['request_id']),
                    agent=agent,
                    program_name=row['program_name'],
                    amount_requested=row['amount_requested'],
                    overhead_cost=row['overhead_cost'],
                    people_benefitted=row['people_benefitted'],
                    duration_months=row['duration_months'],
                    category=ProgramCategory[row['category']],
                    urgency=UrgencyLevel[row['urgency']],
                    sustainability_score=row['sustainability_score'],
                    status=row['status'],
                    succeeded=bool(row['succeeded'])
                )
        return None
    
    def get_all_requests(self, status: Optional[str] = None) -> List[GrantRequest]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute("SELECT * FROM grant_requests WHERE status = ? ORDER BY created_at DESC", (status,))
        else:
            cursor.execute("SELECT * FROM grant_requests ORDER BY created_at DESC")
        
        rows = cursor.fetchall()
        conn.close()
        
        requests = []
        for row in rows:
            agent = self.get_agent(row['agent_id'])
            if agent:
                requests.append(GrantRequest(
                    request_id=str(row['request_id']),
                    agent=agent,
                    program_name=row['program_name'],
                    amount_requested=row['amount_requested'],
                    overhead_cost=row['overhead_cost'],
                    people_benefitted=row['people_benefitted'],
                    duration_months=row['duration_months'],
                    category=ProgramCategory[row['category']],
                    urgency=UrgencyLevel[row['urgency']],
                    sustainability_score=row['sustainability_score'],
                    status=row['status'],
                    succeeded=bool(row['succeeded'])
                ))
        return requests
    
    def update_request_status(self, request_id: int, status: str) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE grant_requests 
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE request_id = ?
        """, (status, request_id))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    
    def mark_request_completed(self, request_id: int, succeeded: bool) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT agent_id FROM grant_requests WHERE request_id = ?", (request_id,))
            row = cursor.fetchone()
            if not row:
                return False
            
            agent_id = row['agent_id']

            cursor.execute("""
                UPDATE grant_requests 
                SET succeeded = ?, updated_at = CURRENT_TIMESTAMP
                WHERE request_id = ?
            """, (1 if succeeded else 0, request_id))

            if succeeded:
                cursor.execute("""
                    UPDATE charity_agents
                    SET total_programs_completed = total_programs_completed + 1,
                        programs_succeeded = programs_succeeded + 1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE agent_id = ?
                """, (agent_id,))
            else:
                cursor.execute("""
                    UPDATE charity_agents
                    SET total_programs_completed = total_programs_completed + 1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE agent_id = ?
                """, (agent_id,))
            
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def delete_request(self, request_id: int) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM grant_requests WHERE request_id = ?", (request_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    
    def get_fund_config(self) -> Dict:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fund_config WHERE id = 1")
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'total_budget': row['total_budget'],
                'allocated_budget': row['allocated_budget'],
                'remaining_budget': row['total_budget'] - row['allocated_budget'],
                'min_allocation_percentage': row['min_allocation_percentage']
            }
        return {}
    
    def update_fund_config(self, total_budget: float = None, 
                          allocated_budget: float = None,
                          min_allocation_percentage: float = None) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if total_budget is not None:
            updates.append("total_budget = ?")
            params.append(total_budget)
        if allocated_budget is not None:
            updates.append("allocated_budget = ?")
            params.append(allocated_budget)
        if min_allocation_percentage is not None:
            updates.append("min_allocation_percentage = ?")
            params.append(min_allocation_percentage)
        
        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            query = f"UPDATE fund_config SET {', '.join(updates)} WHERE id = 1"
            cursor.execute(query, params)
            conn.commit()
            success = cursor.rowcount > 0
        else:
            success = False
        
        conn.close()
        return success
    
    def save_allocation(self, result: FundAllocationResult, strategy_name: str) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO allocation_history 
                (strategy_name, total_budget, total_allocated, remaining_budget,
                 num_fully_funded, num_partially_funded, num_rejected,
                 total_people_benefitted, average_efficiency)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (strategy_name, result.total_budget, result.total_allocated,
                  result.remaining_budget, result.num_fully_funded,
                  result.num_partially_funded, result.num_rejected,
                  result.total_people_benefitted, result.average_efficiency_ratio))
            
            allocation_id = cursor.lastrowid

            for decision in result.decisions:
                cursor.execute("""
                    INSERT INTO allocation_decisions
                    (allocation_id, request_id, amount_allocated, allocation_percentage,
                     priority_score, rank, rationale)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (allocation_id, decision.request.request_id,
                      decision.amount_allocated, decision.allocation_percentage,
                      decision.priority_score, decision.rank, decision.rationale))

                if decision.is_fully_funded() or decision.is_partially_funded():
                    status = 'funded'
                else:
                    status = 'rejected'
                
                cursor.execute("""
                    UPDATE grant_requests 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE request_id = ?
                """, (status, decision.request.request_id))
            
            conn.commit()
            return allocation_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_allocation_history(self, limit: int = 10) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM allocation_history 
            ORDER BY allocation_date DESC 
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                'allocation_id': row['allocation_id'],
                'strategy_name': row['strategy_name'],
                'total_budget': row['total_budget'],
                'total_allocated': row['total_allocated'],
                'remaining_budget': row['remaining_budget'],
                'num_fully_funded': row['num_fully_funded'],
                'num_partially_funded': row['num_partially_funded'],
                'num_rejected': row['num_rejected'],
                'total_people_benefitted': row['total_people_benefitted'],
                'average_efficiency': row['average_efficiency'],
                'allocation_date': row['allocation_date']
            })
        return history
    
    def get_allocation_details(self, allocation_id: int) -> Optional[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM allocation_history 
            WHERE allocation_id = ?
        """, (allocation_id,))
        allocation_row = cursor.fetchone()
        
        if not allocation_row:
            conn.close()
            return None

        cursor.execute("""
            SELECT ad.*, gr.program_name, gr.agent_id, gr.amount_requested, gr.people_benefitted
            FROM allocation_decisions ad
            JOIN grant_requests gr ON ad.request_id = gr.request_id
            WHERE ad.allocation_id = ?
            ORDER BY ad.rank
        """, (allocation_id,))
        decision_rows = cursor.fetchall()

        decisions = []
        for row in decision_rows:
            agent = self.get_agent(row['agent_id'])
            decisions.append({
                'rank': row['rank'],
                'program_name': row['program_name'],
                'agent_name': agent.name if agent else 'Unknown',
                'amount_requested': row['amount_requested'],
                'amount_allocated': row['amount_allocated'],
                'allocation_percentage': row['allocation_percentage'],
                'priority_score': row['priority_score'],
                'people_benefitted': int(row['people_benefitted'] * row['allocation_percentage']),
                'rationale': row['rationale']
            })
        
        conn.close()
        
        return {
            'allocation_id': allocation_row['allocation_id'],
            'strategy_name': allocation_row['strategy_name'],
            'total_budget': allocation_row['total_budget'],
            'total_allocated': allocation_row['total_allocated'],
            'remaining_budget': allocation_row['remaining_budget'],
            'num_fully_funded': allocation_row['num_fully_funded'],
            'num_partially_funded': allocation_row['num_partially_funded'],
            'num_rejected': allocation_row['num_rejected'],
            'total_people_benefitted': allocation_row['total_people_benefitted'],
            'average_efficiency': allocation_row['average_efficiency'],
            'allocation_date': allocation_row['allocation_date'],
            'decisions': decisions
        }

    
    def get_criteria_weights(self) -> Dict[str, float]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM criteria_weights WHERE id = 1")
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'people_benefitted': row['people_benefitted'],
                'efficiency': row['efficiency'],
                'success_rate': row['success_rate'],
                'cost_effectiveness': row['cost_effectiveness'],
                'urgency': row['urgency'],
                'sustainability': row['sustainability'],
                'transparency': row['transparency']
            }
        return {}
    
    def update_criteria_weights(self, weights: Dict[str, float]) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE criteria_weights 
            SET people_benefitted = ?, efficiency = ?, success_rate = ?,
                cost_effectiveness = ?, urgency = ?, sustainability = ?,
                transparency = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = 1
        """, (weights.get('people_benefitted', 0.25),
              weights.get('efficiency', 0.20),
              weights.get('success_rate', 0.15),
              weights.get('cost_effectiveness', 0.15),
              weights.get('urgency', 0.10),
              weights.get('sustainability', 0.10),
              weights.get('transparency', 0.05)))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    
    def get_stats(self) -> Dict:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        cursor.execute("SELECT COUNT(*) as count FROM charity_agents")
        stats['total_agents'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM grant_requests")
        stats['total_requests'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM grant_requests WHERE status = 'pending'")
        stats['pending_requests'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM grant_requests WHERE status = 'funded'")
        stats['funded_requests'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM allocation_history")
        stats['total_allocations'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT SUM(amount_requested) as total FROM grant_requests WHERE status = 'pending'")
        result = cursor.fetchone()
        stats['total_requested'] = result['total'] if result['total'] else 0
        
        conn.close()
        return stats
