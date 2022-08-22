from decimal import Decimal

# Movies and their duration in seconds
movies = {
    "The Shrek Movie": {"duration": 5400,
                        "image": "https://m.media-amazon.com/images/M/MV5BOGZhM2FhNTItODAzNi00YjA0LWEyN2UtNjJlYWQzYzU1MDg5L2ltYWdlL2ltYWdlXkEyXkFqcGdeQXVyMTQxNzMzNDI@._V1_.jpg"},
    "The Little Bee Movie": {"duration": 3360,
                             "image": "https://m.media-amazon.com/images/M/MV5BODk5MDE4MTgzMF5BMl5BanBnXkFtZTgwMzg0OTI5OTE@._V1_FMjpg_UX1000_.jpg"},
    "Ratatoing": {"duration": 2400,
                  "image": "https://m.media-amazon.com/images/M/MV5BODk4MmFiMjAtZDI5NC00YWYzLWI2NjQtMWRlYzUwMDg1ODYwXkEyXkFqcGdeQXVyNjYyNTk4Njk@._V1_FMjpg_UX1000_.jpg"},
    "Chop Kick Panda": {"duration": 2700,
                        "image": "https://m.media-amazon.com/images/M/MV5BMTM4NjQ1Mzk3M15BMl5BanBnXkFtZTgwODc5NTA2MDE@._V1_.jpg"},
    "The Amazing Bulk": {"duration": 4560,
                         "image": "https://m.media-amazon.com/images/M/MV5BMTQ2OTYwMzQwNl5BMl5BanBnXkFtZTgwMzc1NjkyNDE@._V1_FMjpg_UX1000_.jpg"}
}

degrees = {
    'bachelors': {
        'price': Decimal("1000"),
        'stat': Decimal("1"),
        'friendly_name': 'Bachelors Degree'
    },
    'phd': {
        'price': Decimal("2000"),
        'stat': Decimal("3"),
        'friendly_name': 'PhD'
    },
    'bootcamp': {
        'price': Decimal("750"),
        'stat': 0.75,
        'friendly_name': 'Bootcamp Certification of Completion'
    }
}

majors = ["Discriminating Against People Based on their Taste in Music",
          "Throwing it Back",
          "Fortnite Victory Royal Theory",
          "The Industrial Revolution and its Consequences",
          "Twitter Argument De-escalation",
          "Thirst Trapping",
          "Insider Trading",
          "Committing Tax Fraud",
          "Secretly Funding a Proxy War in South America",
          "Roasting Defenseless People on the Internet",
          "Cyberbullying Middle Schoolers",
          "Spreading Misinformation on Facebook",
          "Throwing Batteries into the Ocean",
          "Stealing Catalytic Converters",
          "Simping on the Main",
          "Misleading Investors"]
