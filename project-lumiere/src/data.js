// src/data.js
// This file centralizes all our mock data for movies and tags.

export const movieData = [
    {
        id: 1,
        title: "Avatar",
        year: "2009",
        director: "James Cameron",
        cast: ["Zoe Saldaña", "Sigourney Weaver", "Stephen Lang"],
        runtime: "162 mins",
        genres: ["Science Fiction", "Fantasy"],
        rating: "7.9/10",
        synopsis: "On the lush alien world of Pandora, ex-Marine Jake Sully is thrust into an interstellar conflict between greedy human colonizers and the indigenous Na'vi. Through a genetically engineered avatar body, he learns their ways, falls in love, and must choose between loyalty to his species and the world he has come to call home.",
        streaming: "NETFLIX",
        poster: "https://placehold.co/400x600/9ca3af/ffffff?text=Avatar",
        tags: ["epic", "other-worlds", "spectacle", "romance", "adventure"]
    },
    {
        id: 2,
        title: "Inception",
        year: "2010",
        director: "Christopher Nolan",
        cast: ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Elliot Page"],
        runtime: "148 mins",
        genres: ["Sci-Fi", "Thriller"],
        rating: "8.8/10",
        synopsis: "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
        streaming: "HBO MAX",
        poster: "https://placehold.co/400x600/9ca3af/ffffff?text=Inception",
        tags: ["mind-bending", "heist", "suspenseful", "complex-plot", "dreamy"]
    },
    {
        id: 3,
        title: "Parasite",
        year: "2019",
        director: "Bong Joon Ho",
        cast: ["Song Kang-ho", "Lee Sun-kyun", "Cho Yeo-jeong"],
        runtime: "132 mins",
        genres: ["Thriller", "Comedy", "Drama"],
        rating: "8.6/10",
        synopsis: "Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.",
        streaming: "HULU",
        poster: "https://placehold.co/400x600/9ca3af/ffffff?text=Parasite",
        tags: ["dark-comedy", "social-commentary", "suspenseful", "unpredictable", "satire"]
    },
    {
        id: 4,
        title: "Spirited Away",
        year: "2001",
        director: "Hayao Miyazaki",
        cast: ["Rumi Hiiragi", "Miyu Irino", "Mari Natsuki"],
        runtime: "125 mins",
        genres: ["Animation", "Fantasy"],
        rating: "8.6/10",
        synopsis: "During her family's move to the suburbs, a sullen 10-year-old girl wanders into a world ruled by gods, witches, and spirits, and where humans are changed into beasts.",
        streaming: "HBO MAX",
        poster: "https://placehold.co/400x600/9ca3af/ffffff?text=Spirited+Away",
        tags: ["magical", "coming-of-age", "other-worlds", "bittersweet", "whimsical"]
    },
     {
        id: 5,
        title: "The Grand Budapest Hotel",
        year: "2014",
        director: "Wes Anderson",
        cast: ["Ralph Fiennes", "F. Murray Abraham", "Mathieu Amalric"],
        runtime: "100 mins",
        genres: ["Comedy", "Adventure"],
        rating: "8.1/10",
        synopsis: "The adventures of Gustave H, a legendary concierge at a famous hotel from the fictional Republic of Zubrowka between the first and second World Wars, and Zero Moustafa, the lobby boy who becomes his most trusted friend.",
        streaming: "DISNEY+",
        poster: "https://placehold.co/400x600/9ca3af/ffffff?text=Grand+Budapest",
        tags: ["quirky", "stylized", "dark-comedy", "adventure", "charming"]
    }
];

export const emotionTags = [
    'feel-good', 'thought-provoking', 'inspiring', 'relaxing', 'exciting', 
    'romantic', 'funny', 'sad', 'thrilling', 'mysterious', 'action',
    'comedy', 'drama', 'horror', 'sci-fi', 'romance', 'thriller',
    'documentary', 'animation', 'family'
];
