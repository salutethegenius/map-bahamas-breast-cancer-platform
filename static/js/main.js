document.addEventListener('DOMContentLoaded', function() {
    // Form navigation
    const sections = document.querySelectorAll('.form-section');
    const progressBar = document.querySelector('.progress-bar');
    const registrationForm = document.getElementById('registrationForm');
    
    // Only initialize form navigation if we're on the registration page
    if (registrationForm) {
        let currentSection = 0;

        function validateCurrentSection() {
            const currentFields = sections[currentSection].querySelectorAll('input, select, textarea');
            let isValid = true;
            
            currentFields.forEach(field => {
                if (field.hasAttribute('required') && !field.value) {
                    isValid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            return isValid;
        }

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
                    if (validateCurrentSection() && currentSection < sections.length - 1) {
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

        // Form submission handler
        registrationForm.addEventListener('submit', function(e) {
            try {
                if (!validateCurrentSection()) {
                    e.preventDefault();
                    return false;
                }
                
                const submitBtn = document.getElementById('submit');
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = 'Submitting...';
                }
            } catch (error) {
                console.error('Error handling form submission:', error);
                e.preventDefault();
            }
        });

        // Photo preview
        const photoInput = document.querySelector('input[type="file"]');
        const previewDiv = document.getElementById('photoPreview');

        if (photoInput && previewDiv) {
            photoInput.addEventListener('change', (e) => {
                try {
                    const file = e.target.files[0];
                    if (file) {
                        if (file.size > 16 * 1024 * 1024) { // 16MB limit
                            alert('File size exceeds 16MB limit');
                            e.target.value = '';
                            previewDiv.innerHTML = '';
                            return;
                        }
                        
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
                    } else {
                        previewDiv.innerHTML = '';
                    }
                } catch (error) {
                    console.error('Error handling file upload:', error);
                    previewDiv.innerHTML = '<p class="text-danger">Error handling file</p>';
                }
            });
        }

        // Package selection handler
        const packageSelect = document.querySelector('select[name="package_tier"]');
        if (packageSelect) {
            packageSelect.addEventListener('change', function() {
                try {
                    const isBlackFriday = this.value === 'black_friday';
                    const calendarSection = document.getElementById('calendar-section');
                    if (calendarSection) {
                        const today = new Date();
                        const paymentDate = calendarSection.querySelector('input[type="date"]');
                        if (paymentDate) {
                            paymentDate.min = today.toISOString().split('T')[0];
                        }
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
