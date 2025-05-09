document.addEventListener('DOMContentLoaded', function() {
    // Dashboard initialization function
    function initializeDashboard() {
        try {
            const searchInput = document.getElementById('searchInput');
            const packageFilter = document.getElementById('packageFilter');
            const table = document.getElementById('registrationsTable');

            if (!searchInput || !packageFilter || !table) {
                console.log('Dashboard elements not found - probably not on dashboard page');
                return;
            }

            searchInput.addEventListener('input', filterTable);
            packageFilter.addEventListener('change', filterTable);
        } catch (error) {
            console.error('Error initializing dashboard:', error);
        }
    }

    // Table filtering function
    function filterTable() {
        try {
            const searchInput = document.getElementById('searchInput');
            const packageFilter = document.getElementById('packageFilter');
            const table = document.getElementById('registrationsTable');
            
            if (!searchInput || !packageFilter || !table) {
                console.error('Required elements not found');
                return;
            }

            const tbody = table.getElementsByTagName('tbody')[0];
            if (!tbody) {
                console.error('Table body not found');
                return;
            }

            const searchTerm = searchInput.value.toLowerCase();
            const selectedPackage = packageFilter.value;
            const rows = tbody.getElementsByTagName('tr');

            Array.from(rows).forEach(row => {
                if (!row.cells || row.cells.length < 2) return;

                const companyName = row.cells[0].textContent.toLowerCase();
                const packageTier = row.cells[1].textContent.toLowerCase();

                const matchesSearch = companyName.includes(searchTerm);
                const matchesPackage = !selectedPackage || packageTier.includes(selectedPackage);

                row.style.display = matchesSearch && matchesPackage ? '' : 'none';
            });
        } catch (error) {
            console.error('Error filtering table:', error);
        }
    }

    // View registration details function
    function viewDetails(id) {
        try {
            fetch(`/registration/${id}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.text();
                })
                .then(html => {
                    const modalContent = document.getElementById('modalContent');
                    if (!modalContent) {
                        throw new Error('Modal content element not found');
                    }
                    modalContent.innerHTML = html;
                })
                .catch(error => {
                    console.error('Error:', error);
                    const modalContent = document.getElementById('modalContent');
                    if (modalContent) {
                        modalContent.innerHTML = 'Error loading details';
                    }
                });
        } catch (error) {
            console.error('Error in viewDetails:', error);
        }
    }

    // Export to CSV function
    function exportToCSV() {
        try {
            window.location.href = "/export_registrations";
        } catch (error) {
            console.error('Error exporting to CSV:', error);
        }
    }

    // Form initialization and validation
    function initializeForm() {
        try {
            const sections = document.querySelectorAll('.form-section');
            const progressBar = document.querySelector('.progress-bar');
            const prevBtn = document.getElementById('prev');
            const nextBtn = document.getElementById('next');
            const submitBtn = document.getElementById('submit');
            let currentSection = 0;

            function showSection(sectionIndex) {
                try {
                    sections.forEach((section, index) => {
                        section.classList.remove('active');
                        if (index === sectionIndex) section.classList.add('active');
                    });

                    if (progressBar) {
                        const progress = ((sectionIndex + 1) / sections.length) * 100;
                        progressBar.style.width = progress + '%';
                    }

                    if (prevBtn) prevBtn.style.display = sectionIndex === 0 ? 'none' : 'block';
                    if (nextBtn) nextBtn.style.display = sectionIndex === sections.length - 1 ? 'none' : 'block';
                    if (submitBtn) submitBtn.style.display = sectionIndex === sections.length - 1 ? 'block' : 'none';
                } catch (error) {
                    console.error('Error showing section:', error);
                }
            }

            if (sections.length > 0) {
                if (prevBtn) {
                    prevBtn.addEventListener('click', () => {
                        if (currentSection > 0) {
                            currentSection--;
                            showSection(currentSection);
                        }
                    });
                }

                if (nextBtn) {
                    nextBtn.addEventListener('click', () => {
                        if (validateCurrentSection() && currentSection < sections.length - 1) {
                            currentSection++;
                            showSection(currentSection);
                        }
                    });
                }

                showSection(0);
            }

            // Handle form submission
            const form = document.getElementById('registrationForm');
            if (form) {
                form.addEventListener('submit', function(e) {
                    if (!validateCurrentSection()) {
                        e.preventDefault();
                        return;
                    }
                    
                    // Check if payment date is selected
                    const paymentDate = form.querySelector('input[name="payment_date"]');
                    if (!paymentDate || !paymentDate.value) {
                        e.preventDefault();
                        alert('Please select a payment date');
                        return;
                    }
                });
            }
        } catch (error) {
            console.error('Error initializing form:', error);
        }
    }

    function validateCurrentSection() {
        try {
            const currentForm = document.querySelector('.form-section.active');
            if (!currentForm) return true;

            const fields = currentForm.querySelectorAll('input[required], select[required], textarea[required]');
            let isValid = true;

            fields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('is-invalid');
                    isValid = false;
                } else {
                    field.classList.remove('is-invalid');
                }

                // Additional validation for email fields
                if (field.type === 'email' && field.value.trim()) {
                    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    if (!emailPattern.test(field.value.trim())) {
                        field.classList.add('is-invalid');
                        isValid = false;
                    }
                }

                // Additional validation for phone fields
                if (field.name.includes('phone') && field.value.trim()) {
                    const phonePattern = /^\+?[\d\s-]{7,}$/;
                    if (!phonePattern.test(field.value.trim())) {
                        field.classList.add('is-invalid');
                        isValid = false;
                    }
                }
            });

            return isValid;
        } catch (error) {
            console.error('Error validating form section:', error);
            return false;
        }
    }

    // Photo preview functionality
    function initializePhotoPreview() {
        try {
            const photoInput = document.querySelector('input[type="file"]');
            const previewDiv = document.getElementById('photoPreview');

            if (photoInput && previewDiv) {
                photoInput.addEventListener('change', (e) => {
                    try {
                        const file = e.target.files[0];
                        if (file) {
                            if (file.size > 16 * 1024 * 1024) {
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
                            reader.readAsDataURL(file);
                        } else {
                            previewDiv.innerHTML = '';
                        }
                    } catch (error) {
                        console.error('Error handling file:', error);
                        previewDiv.innerHTML = '';
                    }
                });
            }
        } catch (error) {
            console.error('Error setting up photo preview:', error);
        }
    }

    // Initialize based on page content
    const dashboardTable = document.getElementById('registrationsTable');
    if (dashboardTable) {
        initializeDashboard();
    }

    const registrationForm = document.getElementById('registrationForm');
    if (registrationForm) {
        initializeForm();
        initializePhotoPreview();
    }

    // Make necessary functions available globally
    window.viewDetails = viewDetails;
    window.exportToCSV = exportToCSV;
});
