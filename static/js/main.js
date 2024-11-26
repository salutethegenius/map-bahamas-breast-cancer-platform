document.addEventListener('DOMContentLoaded', function() {
    function initializeDashboard() {
        const searchInput = document.getElementById('searchInput');
        const packageFilter = document.getElementById('packageFilter');
        const table = document.getElementById('registrationsTable');

        if (searchInput && packageFilter && table) {
            try {
                // Search functionality
                searchInput.addEventListener('input', function() {
                    filterTable();
                });

                // Package filter functionality
                packageFilter.addEventListener('change', function() {
                    filterTable();
                });

                function filterTable() {
                    const searchTerm = searchInput.value.toLowerCase();
                    const selectedPackage = packageFilter.value;
                    const rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');

                    Array.from(rows).forEach(row => {
                        const companyName = row.cells[0].textContent.toLowerCase();
                        const packageTier = row.cells[1].textContent.toLowerCase();
                        
                        const matchesSearch = companyName.includes(searchTerm);
                        const matchesPackage = !selectedPackage || packageTier.includes(selectedPackage);
                        
                        row.style.display = matchesSearch && matchesPackage ? '' : 'none';
                    });
                }
            } catch (error) {
                console.error('Error initializing dashboard:', error);
            }
        }
    }

    // Form navigation
    const sections = document.querySelectorAll('.form-section');
    const progressBar = document.querySelector('.progress-bar');
    const prevBtn = document.getElementById('prev');
    const nextBtn = document.getElementById('next');
    const submitBtn = document.getElementById('submit');
    let currentSection = 0;

    function showSection(sectionIndex) {
        sections.forEach((section, index) => {
            section.classList.remove('active');
            if (index === sectionIndex) section.classList.add('active');
        });

        // Update progress bar
        const progress = ((sectionIndex + 1) / sections.length) * 100;
        progressBar.style.width = progress + '%';

        // Update buttons
        prevBtn.style.display = sectionIndex === 0 ? 'none' : 'block';
        nextBtn.style.display = sectionIndex === sections.length - 1 ? 'none' : 'block';
        submitBtn.style.display = sectionIndex === sections.length - 1 ? 'block' : 'none';
    }

    if (prevBtn && nextBtn && submitBtn) {
        prevBtn.addEventListener('click', () => {
            if (currentSection > 0) {
                currentSection--;
                showSection(currentSection);
            }
        });

        nextBtn.addEventListener('click', () => {
            if (currentSection < sections.length - 1) {
                currentSection++;
                showSection(currentSection);
            }
        });

        // Initialize form and dashboard
        showSection(0);
        initializeDashboard();
    }
    
    // Form submission handler (moved here for better structure)
    const registrationForm = document.getElementById('registrationForm');
    if (registrationForm) {
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
    }

    // Photo preview (moved here for better structure)
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

    // Package selection handler (moved here for better structure)
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
});