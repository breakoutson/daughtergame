document.addEventListener('DOMContentLoaded', () => {
    // 게임 데이터
    let coins = 0;
    let playTimeSeconds = 0;
    const items = [
        { id: 'p1', type: 'dress', img: 'assets/pink_dress.png', name: '핑크 드레스' },
        { id: 'p2', type: 'dress', img: 'assets/yellow_dress.png', name: '노랑 드레스' },
        { id: 'a1', type: 'acc', img: 'assets/crown.png', name: '왕관' },
        { id: 'w1', type: 'wings', img: 'assets/wings.png', name: '날개' },
        { id: 's1', type: 'shoes', img: 'assets/shoes.png', name: '구두' }
    ];

    // DOM 요소
    const coinDisplay = document.getElementById('coin-count');
    const timerDisplay = document.getElementById('play-time');
    const player = document.getElementById('player');
    const pet = document.getElementById('pet');
    const petMood = document.getElementById('pet-mood');
    const outfitLayers = document.getElementById('outfit-layers');
    const wardrobeOverlay = document.getElementById('wardrobe-overlay');
    const wardrobeGrid = document.getElementById('wardrobe-grid');
    const magicChest = document.getElementById('magic-chest');
    const fxContainer = document.getElementById('fx-container');

    // --- 1. 경제 시스템 ---
    setInterval(() => {
        playTimeSeconds++;
        const mins = Math.floor(playTimeSeconds / 60).toString().padStart(2, '0');
        const secs = (playTimeSeconds % 60).toString().padStart(2, '0');
        timerDisplay.textContent = `${mins}:${secs}`;

        // 1분마다 10코인 지급
        if (playTimeSeconds % 60 === 0) {
            addCoins(10);
        }
    }, 1000);

    function addCoins(amount) {
        coins += amount;
        coinDisplay.textContent = coins;
        // 코인 애니메이션 (간단히)
        coinDisplay.classList.add('pulse');
        setTimeout(() => coinDisplay.classList.remove('pulse'), 500);
    }

    // --- 2. 펫 시스템 ---
    let petTargetX = 0;
    let petCurrentX = 0;

    // 펫이 플레이어를 따라오게 함
    setInterval(() => {
        // 플레이어 근처로 슬금슬금
        petCurrentX += (petTargetX - petCurrentX) * 0.1;
        pet.style.transform = `translateX(${petCurrentX}px)`;
    }, 30);

    // 펫 무드 관리
    const moods = ['🍔', '💤', '❤️', '🧶'];
    setInterval(() => {
        petMood.textContent = moods[Math.floor(Math.random() * moods.length)];
    }, 10000);

    pet.addEventListener('click', () => {
        createHearts(pet.getBoundingClientRect().left + 30, pet.getBoundingClientRect().top);
        pet.animate([
            { transform: `translateX(${petCurrentX}px) translateY(0)` },
            { transform: `translateX(${petCurrentX}px) translateY(-30px)` },
            { transform: `translateX(${petCurrentX}px) translateY(0)` }
        ], { duration: 500, easing: 'ease-out' });
        petMood.textContent = '❤️';
    });

    // --- 3. 옷 꾸미기 시스템 ---
    document.getElementById('open-wardrobe').addEventListener('click', () => {
        renderWardrobe('dress');
        wardrobeOverlay.classList.add('active');
    });

    document.querySelectorAll('.close-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            wardrobeOverlay.classList.remove('active');
        });
    });

    function renderWardrobe(category) {
        wardrobeGrid.innerHTML = '';
        items.filter(i => i.type === category).forEach(item => {
            const div = document.createElement('div');
            div.className = 'grid-item';
            div.innerHTML = `<img src="${item.img}" alt="${item.name}">`;
            div.addEventListener('click', () => {
                applyItem(item);
                createHearts(window.innerWidth / 2, window.innerHeight / 2);
            });
            wardrobeGrid.appendChild(div);
        });

        // 탭 활성화 상태 변경
        document.querySelectorAll('.cat-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.cat === category);
        });
    }

    document.querySelectorAll('.cat-btn').forEach(btn => {
        btn.addEventListener('click', () => renderWardrobe(btn.dataset.cat));
    });

    function applyItem(item) {
        let layer = outfitLayers.querySelector(`.layer-${item.type}`);
        if (!layer) {
            layer = document.createElement('img');
            layer.className = `layer-item layer-${item.type}`;
            outfitLayers.appendChild(layer);
        }
        layer.src = item.img;
    }

    // --- 4. 보물 상자 ---
    magicChest.addEventListener('click', () => {
        if (coins >= 50) {
            coins -= 50;
            coinDisplay.textContent = coins;
            openChest();
        } else {
            alert('코인이 더 필요해요! 💰 (50코인 필요)');
        }
    });

    function openChest() {
        // 상자 애니메이션
        magicChest.animate([
            { transform: 'scale(1) rotate(0)' },
            { transform: 'scale(1.2) rotate(5deg)' },
            { transform: 'scale(1.2) rotate(-5deg)' },
            { transform: 'scale(1) rotate(0)' }
        ], { duration: 500 });

        setTimeout(() => {
            alert('짜잔! 새로운 아이템을 발견했을지도 몰라요! ✨ (다음 버전에 추가 예정)');
            createConfetti();
        }, 500);
    }

    // --- 효과 함수들 ---
    function createHearts(x, y) {
        for (let i = 0; i < 5; i++) {
            const heart = document.createElement('div');
            heart.className = 'particle-heart';
            heart.textContent = '❤️';
            heart.style.left = `${x}px`;
            heart.style.top = `${y}px`;
            fxContainer.appendChild(heart);

            heart.animate([
                { transform: 'translate(0,0) scale(1)', opacity: 1 },
                { transform: `translate(${(Math.random() - 0.5) * 100}px, -100px) scale(0)`, opacity: 0 }
            ], { duration: 1000, easing: 'ease-out' }).onfinish = () => heart.remove();
        }
    }

    function createConfetti() {
        for (let i = 0; i < 30; i++) {
            const c = document.createElement('div');
            c.className = 'particle-heart';
            c.style.background = `hsl(${Math.random() * 360}, 100%, 70%)`;
            c.style.width = '10px'; c.style.height = '10px';
            c.style.left = '50%'; c.style.top = '50%';
            fxContainer.appendChild(c);

            c.animate([
                { transform: 'translate(0,0)', opacity: 1 },
                { transform: `translate(${(Math.random() - 0.5) * 500}px, ${(Math.random() - 0.5) * 500}px) rotate(${Math.random() * 360}deg)`, opacity: 0 }
            ], { duration: 2000 }).onfinish = () => c.remove();
        }
    }
});
