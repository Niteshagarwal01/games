// Global variables
let currentPage = 1;
const gamesPerPage = 6;
let currentGame = null;

// DOM Elements
const gameContainer = document.getElementById('game-container');
const prevPageBtn = document.getElementById('prev-page');
const nextPageBtn = document.getElementById('next-page');
const pageIndicator = document.getElementById('page-indicator');
const gameModal = document.getElementById('game-modal');
const modalGameTitle = document.getElementById('modal-game-title');
const modalGameImage = document.getElementById('modal-game-image');
const modalGameDesc = document.getElementById('modal-game-desc');
const closeButton = document.querySelector('.close-button');
const playGameBtn = document.getElementById('play-game');
const backButton = document.getElementById('back-button');
const gamePlayer = document.getElementById('game-player');
const gameIframe = document.getElementById('game-iframe');
const playingGameTitle = document.getElementById('playing-game-title');
const exitGameBtn = document.getElementById('exit-game');

// Initialize the game launcher
function initGameLauncher() {
    displayGames();
    setupEventListeners();
}

// Display games for the current page
function displayGames() {
    gameContainer.innerHTML = '';
    
    const startIndex = (currentPage - 1) * gamesPerPage;
    const endIndex = Math.min(startIndex + gamesPerPage, games.length);
    
    for (let i = startIndex; i < endIndex; i++) {
        const game = games[i];
        
        // Create game card
        const gameCard = document.createElement('div');
        gameCard.className = 'game-card';
        gameCard.dataset.gameId = game.id;
        
        // Check if thumbnail path exists
        const thumbnailHtml = game.thumbnail 
            ? `<img src="${game.thumbnail}" alt="${game.title}" class="game-thumbnail">`
            : `<div class="no-image">No Preview Available</div>`;
        
        gameCard.innerHTML = `
            ${thumbnailHtml}
            <div class="game-info">
                <div class="game-title">${game.title}</div>
            </div>
        `;
        
        gameCard.addEventListener('click', () => openGameDetails(game));
        gameContainer.appendChild(gameCard);
    }
    
    // Update pagination controls
    updatePagination();
}

// Update pagination buttons and indicator
function updatePagination() {
    const totalPages = Math.ceil(games.length / gamesPerPage);
    pageIndicator.textContent = `Page ${currentPage}/${totalPages}`;
    
    prevPageBtn.disabled = currentPage === 1;
    nextPageBtn.disabled = currentPage >= totalPages;
}

// Open game details modal
function openGameDetails(game) {
    currentGame = game;
    
    modalGameTitle.textContent = game.title;
    modalGameDesc.textContent = game.description;
    
    // Use the thumbnail or first screenshot if available
    const imageUrl = game.thumbnail || (game.screenshots && game.screenshots.length > 0 ? game.screenshots[0] : '');
    if (imageUrl) {
        modalGameImage.src = imageUrl;
        modalGameImage.style.display = 'block';
    } else {
        modalGameImage.style.display = 'none';
    }
    
    gameModal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

// Close game details modal
function closeGameDetails() {
    gameModal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Play selected game
function playGame() {
    if (!currentGame) return;
    
    gameModal.style.display = 'none';
    gamePlayer.classList.remove('hidden');
    
    // Set up the game iframe with the game URL
    gameIframe.src = currentGame.playUrl;
    playingGameTitle.textContent = `Playing: ${currentGame.title}`;
    
    document.body.style.overflow = 'hidden';
}

// Exit game and return to launcher
function exitGame() {
    gamePlayer.classList.add('hidden');
    gameIframe.src = '';
    document.body.style.overflow = 'auto';
}

// Setup event listeners
function setupEventListeners() {
    prevPageBtn.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            displayGames();
        }
    });
    
    nextPageBtn.addEventListener('click', () => {
        const totalPages = Math.ceil(games.length / gamesPerPage);
        if (currentPage < totalPages) {
            currentPage++;
            displayGames();
        }
    });
    
    closeButton.addEventListener('click', closeGameDetails);
    backButton.addEventListener('click', closeGameDetails);
    playGameBtn.addEventListener('click', playGame);
    exitGameBtn.addEventListener('click', exitGame);
    
    // Close modal when clicking outside of it
    window.addEventListener('click', (e) => {
        if (e.target === gameModal) {
            closeGameDetails();
        }
    });
    
    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            if (gamePlayer.classList.contains('hidden') === false) {
                exitGame();
            } else if (gameModal.style.display === 'block') {
                closeGameDetails();
            }
        } else if (e.key === 'ArrowLeft') {
            if (gameModal.style.display !== 'block' && gamePlayer.classList.contains('hidden') && currentPage > 1) {
                currentPage--;
                displayGames();
            }
        } else if (e.key === 'ArrowRight') {
            if (gameModal.style.display !== 'block' && gamePlayer.classList.contains('hidden')) {
                const totalPages = Math.ceil(games.length / gamesPerPage);
                if (currentPage < totalPages) {
                    currentPage++;
                    displayGames();
                }
            }
        }
    });
}

// Initialize when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', initGameLauncher);