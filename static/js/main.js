document.addEventListener('DOMContentLoaded', function() {
    // Form navigation
    const sections = document.querySelectorAll('.form-section');
    const progressBar = document.querySelector('.progress-bar');
    let currentSection = 0;

    function updateProgress() {
        const progress = ((currentSection + 1) / sections.length) * 100;
        progressBar.style.width = progress + '%';
    }

    function showSection(index) {
        sections.forEach(section => section.classList.remove('active'));
        sections[index].classList.add('active');
        
        // Update navigation buttons
        const prevBtn = document.getElementById('prev');
        const nextBtn = document.getElementById('next');
        const submitBtn = document.getElementById('submit');
        
        prevBtn.style.display = index === 0 ? 'none' : 'block';
        nextBtn.style.display = index === sections.length - 1 ? 'none' : 'block';
        submitBtn.style.display = index === sections.length - 1 ? 'block' : 'none';
        
        updateProgress();
    }

    // Next button handler
    document.getElementById('next').addEventListener('click', function() {
        if (currentSection < sections.length - 1) {
            currentSection++;
            showSection(currentSection);
        }
    });

    // Previous button handler
    document.getElementById('prev').addEventListener('click', function() {
        if (currentSection > 0) {
            currentSection--;
            showSection(currentSection);
        }
    });

    // Photo preview
    const photoInput = document.querySelector('input[type="file"]');
    const previewDiv = document.getElementById('photoPreview');

    photoInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                previewDiv.innerHTML = `
                    <img src="${e.target.result}" 
                         alt="Contact photo preview" 
                         style="max-width: 200px; max-height: 200px; border-radius: 4px;">`;
            };
            reader.readAsDataURL(file);
        }
    });

    // Package selection handler
    const packageSelect = document.querySelector('select[name="package_tier"]');
    packageSelect.addEventListener('change', function() {
        const isBlackFriday = this.value === 'black_friday';
        const priceDisplay = document.querySelector('.package-price');
        if (priceDisplay) {
            priceDisplay.innerHTML = isBlackFriday ? '50% OFF!' : '';
        }
    });

    // Initialize form
    showSection(0);
});
