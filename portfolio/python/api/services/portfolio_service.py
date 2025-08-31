from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.database.models import Portfolio, Asset, Transaction
from schemas.portfolio import PortfolioCreate, PortfolioUpdate

class PortfolioService:
    """Service for portfolio operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_portfolio(self, portfolio_data: PortfolioCreate) -> Portfolio:
        """Create a new portfolio."""
        portfolio = Portfolio(**portfolio_data.dict())
        self.db.add(portfolio)
        self.db.commit()
        self.db.refresh(portfolio)
        return portfolio
    
    def get_user_portfolios(self, user_id: int) -> List[Portfolio]:
        """Get all portfolios for a user."""
        return self.db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
    
    def get_portfolio(self, portfolio_id: int) -> Optional[Portfolio]:
        """Get a specific portfolio by ID."""
        return self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    
    def update_portfolio(self, portfolio_id: int, portfolio_data: PortfolioUpdate) -> Optional[Portfolio]:
        """Update a portfolio."""
        portfolio = self.get_portfolio(portfolio_id)
        if portfolio:
            for field, value in portfolio_data.dict(exclude_unset=True).items():
                setattr(portfolio, field, value)
            self.db.commit()
            self.db.refresh(portfolio)
        return portfolio
