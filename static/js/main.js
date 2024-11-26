document.addEventListener('DOMContentLoaded', function() {
    // Form navigation
    const sections = document.querySelectorAll('.form-section');
    const progressBar = document.querySelector('.progress-bar');
    const registrationForm = document.getElementById('registrationForm');
    
    // Only initialize form navigation if we're on the registration page
    if (registrationForm) {
        let currentSection = 0;

        function updateProgress() {
            if (progressBar) {
                const progress = ((currentSection + 1) / sections.length) * 100;
                progressBar.style.width = `${progress}%`;
            }
        }

        function showSection(index) {
            sections.forEach(section => section.classList.remove('active'));
            sections[index].classList.add('active');
            
            // Update navigation buttons
            const prevBtn = document.getElementById('prev');
            const nextBtn = document.getElementById('next');
            const submitBtn = document.getElementById('submit');
            
            if (prevBtn && nextBtn && submitBtn) {
                prevBtn.style.display = index === 0 ? 'none' : 'block';
                nextBtn.style.display = index === sections.length - 1 ? 'none' : 'block';
                submitBtn.style.display = index === sections.length - 1 ? 'block' : 'none';
            }
            
            updateProgress();
        }

        // Initialize navigation buttons
        const nextBtn = document.getElementById('next');
        const prevBtn = document.getElementById('prev');

        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                try {
                    if (currentSection < sections.length - 1) {
                        currentSection++;
                        showSection(currentSection);
                    }
                } catch (error) {
                    console.error('Error navigating to next section:', error);
                }
            });
        }

        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                try {
                    if (currentSection > 0) {
                        currentSection--;
                        showSection(currentSection);
                    }
                } catch (error) {
                    console.error('Error navigating to previous section:', error);
                }
            });
        }

        // Photo preview
        const photoInput = document.querySelector('input[type="file"]');
        const previewDiv = document.getElementById('photoPreview');

        if (photoInput && previewDiv) {
            photoInput.addEventListener('change', (e) => {
                try {
                    const file = e.target.files[0];
                    if (file) {
                        const reader = new FileReader();
                        reader.onload = (e) => {
                            previewDiv.innerHTML = `
                                <img src="${e.target.result}" 
                                     alt="Contact photo preview" 
                                     style="max-width: 200px; max-height: 200px; border-radius: 4px;">`;
                        };
                        reader.onerror = (error) => {
                            console.error('Error reading file:', error);
                            previewDiv.innerHTML = '<p class="text-danger">Error loading preview</p>';
                        };
                        reader.readAsDataURL(file);
                    }
                } catch (error) {
                    console.error('Error handling file upload:', error);
                }
            });
        }

        // Package selection handler
        const packageSelect = document.querySelector('select[name="package_tier"]');
        if (packageSelect) {
            packageSelect.addEventListener('change', function() {
                try {
                    const isBlackFriday = this.value === 'black_friday';
                    const priceDisplay = document.querySelector('.package-price');
                    if (priceDisplay) {
                        priceDisplay.innerHTML = isBlackFriday ? '50% OFF!' : '';
                    }
                } catch (error) {
                    console.error('Error handling package selection:', error);
                }
            });
        }

        // Initialize form
        showSection(0);
    }
});
