from dataclasses import dataclass

@dataclass
class PrizesRemaining():
    amount: float
    start: int
    remaining: int
    def __post_init__(self):
        # clean any strings with regex to get only numbers
        self.amount = float(self.amount.replace("$", "").replace(",", ""))
@dataclass
class Ticket():
    name: str
    price: float
    top_prize: float
    remaining_top_prizes: int
    chances_to_win: int
    game_start_date: str
    last_date_to_claim: str
    probability: float
    prizes_remaining: list[PrizesRemaining]
    
    prizes_remaining_link: str

    def __post_init__(self):
        # clean any strings with regex to get only numbers
        self.price = float(self.price.replace("$", ""))
        self.top_prize = float(self.top_prize.replace("$", "").replace(",", ""))
        self.probability = float(self.probability.split(" in ")[1])

