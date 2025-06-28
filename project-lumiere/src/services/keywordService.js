// src/services/keywordService.js
// Service for loading and searching keywords from the CSV file

class KeywordService {
    constructor() {
        this.allKeywords = [];
        this.isLoaded = false;
    }

    async loadAllKeywords() {
        if (this.isLoaded) {
            return this.allKeywords;
        }

        try {
            // In a real app, you'd fetch this from an API endpoint
            // For now, we'll create a mock implementation
            // This would typically be loaded from the backend API
            
            // Mock data - in production this would come from the CSV file via API
            const mockKeywords = [
                { keyword: 'individual', id: 30 },
                { keyword: 'holiday', id: 65 },
                { keyword: 'germany', id: 74 },
                { keyword: 'gunslinger', id: 75 },
                { keyword: 'saving the world', id: 83 },
                { keyword: 'paris, france', id: 90 },
                { keyword: 'slum', id: 100 },
                { keyword: 'barcelona, spain', id: 107 },
                { keyword: 'transvestism', id: 108 },
                { keyword: 'venice, italy', id: 110 },
                { keyword: 'holy grail', id: 113 },
                { keyword: 'love triangle', id: 128 },
                { keyword: 'italy', id: 131 },
                { keyword: 'anti terror', id: 139 },
                { keyword: 'christianity', id: 186 },
                { keyword: 'islam', id: 187 },
                { keyword: 'buddhism', id: 188 },
                { keyword: 'bureaucracy', id: 211 },
                { keyword: 'london, england', id: 212 },
                { keyword: 'upper class', id: 213 },
                { keyword: 'berlin, germany', id: 220 },
                { keyword: 'schizophrenia', id: 222 },
                { keyword: 'japan', id: 233 },
                { keyword: 'suicide', id: 236 },
                { keyword: 'underdog', id: 240 },
                { keyword: 'new york city', id: 242 },
                { keyword: 'dancing', id: 246 },
                { keyword: 'date', id: 248 },
                { keyword: 'france', id: 254 },
                { keyword: 'bomb', id: 258 },
                { keyword: 'amputation', id: 259 },
                { keyword: 'disillusion', id: 260 },
                { keyword: 'diving', id: 269 },
                { keyword: 'ocean', id: 270 },
                { keyword: 'competition', id: 271 },
                { keyword: 'transylvania', id: 272 },
                { keyword: 'philadelphia, pennsylvania', id: 276 },
                { keyword: 'stockholm syndrome', id: 278 },
                { keyword: 'video game', id: 282 },
                { keyword: 'angel', id: 290 },
                { keyword: 'circus', id: 291 },
                { keyword: 'berlin wall', id: 292 },
                { keyword: 'library', id: 295 },
                { keyword: 'moon', id: 305 },
                { keyword: 'jupiter', id: 306 },
                { keyword: 'artificial intelligence (a.i.)', id: 310 },
                { keyword: 'human evolution', id: 311 },
                { keyword: 'man vs machine', id: 312 },
                { keyword: 'life and death', id: 314 },
                { keyword: 'chess', id: 316 },
                { keyword: 'police state', id: 318 },
                { keyword: 'raf (royal air force)', id: 323 },
                { keyword: 'portugal', id: 324 },
                { keyword: 'insulin', id: 328 },
                { keyword: 'tattoo', id: 331 },
                { keyword: 'insect', id: 332 },
                { keyword: 'mushroom', id: 333 },
                { keyword: 'flying', id: 334 },
                { keyword: 'submarine', id: 339 },
                { keyword: 'inquisition', id: 344 },
                { keyword: 'monk', id: 345 },
                { keyword: 'aristotle', id: 347 },
                { keyword: 'poison', id: 351 },
                { keyword: 'secret passage', id: 352 },
                { keyword: 'ghost train', id: 365 },
                { keyword: 'sex shop', id: 366 },
                { keyword: 'shyness', id: 367 },
                { keyword: 'arms smuggling', id: 374 },
                { keyword: 'neo-nazism', id: 376 },
                { keyword: 'prison', id: 378 },
                { keyword: 'skinhead', id: 379 },
                { keyword: 'sibling relationship', id: 380 },
                { keyword: 'poker', id: 383 },
                { keyword: 'jules verne', id: 385 },
                { keyword: 'california', id: 387 },
                { keyword: 'scotland', id: 388 },
                { keyword: 'clock tower', id: 389 },
                { keyword: 'skateboarding', id: 390 },
                { keyword: 'flying car', id: 391 },
                { keyword: 'england', id: 392 },
                { keyword: 'civil war', id: 393 },
                { keyword: 'gypsy', id: 394 },
                { keyword: 'gambling', id: 395 },
                { keyword: 'transporter', id: 396 },
                { keyword: 'bare knuckle boxing', id: 397 },
                { keyword: 'slang', id: 398 },
                { keyword: 'fountain of youth', id: 399 },
                { keyword: 'clone', id: 402 },
                { keyword: 'dictator', id: 407 },
                { keyword: 'africa', id: 409 },
                { keyword: 'hunter', id: 414 },
                { keyword: 'miami, florida', id: 416 },
                { keyword: 'corruption', id: 417 },
                { keyword: 'white russian', id: 418 },
                { keyword: 'bowling', id: 420 },
                { keyword: 'vietnam veteran', id: 422 },
                { keyword: 'nurse', id: 428 },
                { keyword: 'venezuela', id: 430 },
                { keyword: 'destruction of a civilization', id: 434 },
                { keyword: 'south seas', id: 436 },
                { keyword: 'painter', id: 437 },
                { keyword: 'paradise', id: 439 },
                { keyword: 'missionary', id: 440 },
                { keyword: 'assassination', id: 441 },
                { keyword: 'taxi', id: 444 },
                { keyword: 'pornography', id: 445 },
                { keyword: 'post-traumatic stress disorder (ptsd)', id: 447 },
                { keyword: 'yugoslavia', id: 449 },
                { keyword: 'farewell', id: 455 },
                { keyword: 'mother', id: 456 },
                { keyword: 'hippie', id: 458 },
                { keyword: 'sexual obsession', id: 459 },
                { keyword: 'free love', id: 460 },
                { keyword: 'swinger club', id: 463 },
                { keyword: 'total destruction', id: 464 },
                { keyword: 'megacity', id: 467 },
                { keyword: 'spy', id: 470 },
                { keyword: 'bathroom', id: 472 },
                { keyword: 'chain', id: 473 },
                { keyword: 'self-fulfilling prophecy', id: 476 },
                { keyword: 'china', id: 478 },
                { keyword: 'imperator', id: 481 },
                { keyword: 'riddle', id: 483 },
                { keyword: 'nepal', id: 485 },
                { keyword: 'himalaya mountain range', id: 486 },
                { keyword: 'cairo', id: 487 },
                { keyword: 'moses', id: 488 },
                { keyword: 'philosophy', id: 490 },
                { keyword: 'poem', id: 493 },
                { keyword: 'scapegoat', id: 495 },
                { keyword: 'poetry', id: 496 },
                { keyword: 'ambush', id: 502 },
                { keyword: 'nudist camp', id: 508 },
                { keyword: 'denmark', id: 509 },
                { keyword: 'spain', id: 514 },
                { keyword: 'child abuse', id: 516 },
                { keyword: 'chicago, illinois', id: 520 },
                { keyword: 'washington dc, usa', id: 521 },
                { keyword: 'borg', id: 522 },
                { keyword: 'foreigner', id: 525 },
                { keyword: 'rebel', id: 526 },
                { keyword: 'ku klux klan', id: 529 },
                { keyword: 'prophecy', id: 530 },
                { keyword: 'southern usa', id: 531 },
                { keyword: 'music record', id: 532 },
                { keyword: 'mexico', id: 534 },
                { keyword: 'israel', id: 536 },
                { keyword: 'palestine', id: 537 },
                { keyword: 'middle east', id: 539 },
                { keyword: 'street gang', id: 542 },
                { keyword: 'sailboat', id: 544 },
                { keyword: 'countryside', id: 548 },
                { keyword: 'prostitute', id: 549 },
                { keyword: 'call girl', id: 550 },
                { keyword: 'manager', id: 554 },
                { keyword: 'city portrait', id: 558 },
                { keyword: 'peace conference', id: 559 },
                { keyword: 'oxygen', id: 560 },
                { keyword: 'deja vu', id: 563 },
                { keyword: 'sexual identity', id: 566 },
                { keyword: 'alcohol', id: 567 },
                { keyword: 'rape', id: 570 },
                { keyword: 'transsexuality', id: 571 },
                { keyword: 'rock \'n\' roll', id: 578 },
                { keyword: 'american football', id: 579 },
                { keyword: 'san francisco, california', id: 582 },
                { keyword: 'perfect crime', id: 584 },
                { keyword: 'casino', id: 585 },
                { keyword: 'new jersey', id: 586 },
                { keyword: 'amsterdam, netherlands', id: 587 },
                { keyword: 'rome, italy', id: 588 },
                { keyword: 'central intelligence agency (cia)', id: 591 },
                { keyword: 'capitalism', id: 592 },
                { keyword: 'globalization', id: 593 },
                { keyword: 'adultery', id: 596 },
                { keyword: 'elves', id: 603 },
                { keyword: 'dwarf', id: 604 },
                { keyword: 'orcs', id: 606 },
                { keyword: 'hotel', id: 612 },
                { keyword: 'new year\'s eve', id: 613 },
                { keyword: 'witch', id: 616 },
                { keyword: 'shire', id: 617 },
                { keyword: 'rivendell', id: 619 },
                { keyword: 'bet', id: 622 },
                { keyword: 'sadistic', id: 625 },
                { keyword: 'killing', id: 627 },
                { keyword: 'sicily, italy', id: 629 },
                { keyword: 'dolphin', id: 630 },
                { keyword: 'apnoe-diving', id: 631 },
                { keyword: 'disc jockey', id: 635 },
                { keyword: 'pop', id: 637 },
                { keyword: 'transvestite', id: 640 },
                { keyword: 'single parent', id: 641 },
                { keyword: 'robbery', id: 642 },
                { keyword: 'horse race', id: 643 },
                { keyword: 'gymnastics', id: 650 },
                { keyword: 'candelabrum', id: 651 },
                { keyword: 'fire', id: 657 },
                { keyword: 'sea', id: 658 }
            ];

            this.allKeywords = mockKeywords;
            this.isLoaded = true;
            
            return this.allKeywords;
        } catch (error) {
            console.error('Failed to load keywords:', error);
            return [];
        }
    }

    async searchKeywords(query, limit = 10) {
        if (!query || query.trim() === '') {
            return [];
        }
        try {
            const response = await fetch(`http://localhost:8000/keywords/search?q=${encodeURIComponent(query)}&limit=${limit}`);
            if (!response.ok) {
                throw new Error('Failed to fetch search results');
            }
            const data = await response.json();
            return data.results || [];
        } catch (error) {
            console.error('Keyword search failed:', error);
            return [];
        }
    }

    async getKeywordById(id) {
        await this.loadAllKeywords();
        return this.allKeywords.find(keyword => keyword.id === id);
    }

    async getKeywordByName(name) {
        await this.loadAllKeywords();
        return this.allKeywords.find(keyword => 
            keyword.keyword.toLowerCase() === name.toLowerCase()
        );
    }
}

export default new KeywordService(); 