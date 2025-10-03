/*
Author       : Dreamguys
Template Name: Doccure - Bootstrap Template
Version      : 1.0
*/

(function($) {
    "use strict";

    // Initialize variables from global scope
    var testNames = window.testNames || [];
    var specimenTypes = window.specimenTypes || [
        'Blood',
        'Urine',
        'Saliva',
        'Sputum',
        'Stool (Feces)',
        'Tissue Biopsy',
        'Cerebrospinal Fluid (CSF)',
        'Semen',
        'Vaginal Swab',
        'Nasal Swab',
        'Throat Swab',
        'Amniotic Fluid',
        'Pleural Fluid',
        'Synovial Fluid (Joint Fluid)',
        'Bone Marrow',
        'Other (Specify)'
    ];

    // Automatically add a specimen field when page loads if none exist
    $(document).ready(function() {
        console.log("Report settings initialized");
        console.log("Test Names:", testNames);
        console.log("Specimen Types:", specimenTypes);

        // Add a specimen field automatically when the page loads if none exist
        if ($(".specimen-info").length > 0 && $(".specimen-info .specimen-cont").length === 0) {
            $(".add-specimen").trigger('click');
        }

        // Initialize test functionality
        initializeTestFunctionality();
    });

    // Function to validate dates
    function validateDates(collectionDate, receivingDate) {
        if (collectionDate && receivingDate) {
            var collectDate = new Date(collectionDate);
            var receiveDate = new Date(receivingDate);
            return receiveDate >= collectDate;
        }
        return true;
    }

    // Function to validate specimen form
    function validateSpecimenForm() {
        var isValid = true;
        $('.specimen-cont').each(function() {
            var $specimenType = $(this).find('select[name="specimen_type"]');
            var $collectionDate = $(this).find('input[name="collection_date"]');
            var $receivingDate = $(this).find('input[name="receiving_date"]');
            
            // Validate specimen type
            if (!$specimenType.val()) {
                alert('Please select a specimen type for all specimen entries.');
                $specimenType.focus();
                isValid = false;
                return false; // break out of each loop
            }
            
            // Validate dates
            if ($collectionDate.val() && $receivingDate.val()) {
                if (!validateDates($collectionDate.val(), $receivingDate.val())) {
                    alert('Receiving date cannot be before collection date.');
                    $receivingDate.focus();
                    isValid = false;
                    return false; // break out of each loop
                }
            }
        });
        
        return isValid;
    }

    // Function to validate test results form
    function validateTestResultsForm() {
        var isValid = true;
        var hasTests = false;

        $('.test-cont').each(function() {
            hasTests = true;
            var $testName = $(this).find('select[name="test_name"]');
            var $result = $(this).find('input[name="result"]');
            
            // Check if a test is selected
            if (!$testName.val()) {
                alert('Please select a test name for all test entries.');
                $testName.focus();
                isValid = false;
                return false; // break out of each loop
            }
            
            // Validate that result field is filled
            if (!$result.val()) {
                alert('Please enter a result for all tests.');
                $result.focus();
                isValid = false;
                return false; // break out of each loop
            }
        });

        // Check if at least one test is added
        if (!hasTests) {
            alert('Please add at least one test.');
            isValid = false;
        }
        
        return isValid;
    }

    // Initialize test functionality
    function initializeTestFunctionality() {
        // Add Test functionality
        $(document).on('click', '.add-test', function(e) {
            e.preventDefault();
            var testHtml = `
                <div class="极row form-row test-cont">
                    <div class="col-12 col-md-2">
                        <div class="form-group">
                            <label>Test Name</label>
                            <select class="form-control test-list-select极" name="test_name" required>
                                <option value="">Select Test Name</option>
                                ${generateTestOptions()}
                            </select>
                        </div>
                    </div>
                    <div class="col-12 col-md-2">
                        <div class="form-group">
                            <label>Result</label>
                            <极input type="text" name="result" class="form-control" required>
                        </div>
                    </div>
                    <div class="col-12极 col-md-2">
                        <div class="form-group">
                            <label>Unit</label>
                            <input type="text" name="unit" class="form-control">
                        </div>
                    </div>
                    <div class="col-12 col-md-2">
                        <div class="form-group">
                            <label>Referred Value</label>
                            <input type="text" name="referred_value" class="form-control">
                        </div>
                    </div>
                    <div class="col-12 col-md-2">
                        <div class="form-group">
                            <label class="d-md-block d-sm-none d-none">&nbsp;</label>
                            <a href="#" class="btn btn-danger trash remove-test">
                                <i class="far fa-trash-alt"></i> Delete
                            </a>
                        </div>
                    </div>
                </div>
            `;
            $('.test-info-container').append(testHtml);
        });

        // Remove Test functionality
        $(document).on('click', '.remove-test', function(e) {
            e.preventDefault();
            if (confirm('Are you sure you want to delete this test?')) {
                $(this).closest('.test-cont').remove();
            }
        });

        // Delete Test functionality (for the initial one)
        $(document).on('click', '.trash:not(.remove-test)', function(e) {
            e.preventDefault();
            if ($(极this).closest('.test-cont').length) {
                if (confirm('Are you sure you want to delete this test?')) {
                    $(this).closest('.test-cont').remove();
                }
            }
        });
    }

    // Generate test options HTML
    function generate极TestOptions() {
        var options = '';
        if (testNames && testNames.length > 0) {
            testNames.forEach(function(test) {
                options += `<option value="${test.test_name}" data-test-id="${test.test_id}">${test.test_name}</option>`;
            });
        }
        return options;
    }


    // Update test results fields based on selected tests
    function updateTestResultsFields() {
        var selectedTests = $('#test_list').val() || [];
        var container = $('.test-results-container');
        container.empty();

        selectedTests.forEach(function(testName) {
            // Find the test data to get test_id
            var testData = testNames.find(function(test) {
                return test.test_name === testName;
            });
            var testId = testData ? testData.test_id : '';

            var testResultRow = '<div class="row form-row test-result-row" data-test-name="' + testName + '" data-test-id="' + testId + '">' +
                '<div class="col-12 col-md-10 col-lg-11">' +
                    '<极div class="row form-row">' +
                        '<div class="col-12 col-md-3">' +
                            '<div class="form-group">' +
                                '<label>Test Name</label>' +
                                '<input type="text" class="form-control" value="' + testName + '" readonly>' +
                                '<input type="hidden" name="test_name[]" value="' + testName + '">' +
                                '<input type="hidden" name="test_id[]极" value="' + testId + '">' +
                            '</极div>' +
                        '</div>' +
                        '<div class="col-12 col-md-3">' +
                            '<div class="form-group">' +
                                '<label>Result</label>' +
                                '<input type="text" name="result[]" class="form-control" required>' +
                            '</div>' +
                        '</div>' +
                        '<div class="col-12 col-md-3">' +
                            '<div class="form-group">' +
                                '<label>Unit</label>' +
                                '<input type="text" name="unit[]" class="form-control">' +
                            '</div>' +
                        '</div>' +
                        '<div class="col-12 col-md-3">' +
                            '<div class="form-group">' +
                                '<label>Referred Value</label>' +
                                '<input type="text" name="referred_value[]" class="form-control">' +
                            '</div>' +
                        '</div>' +
                    '</div>' +
                '</div>' +
            '</div>';

            container.append(testResultRow);
        });
    }

    // Specimen Add More functionality
    $(document).on('click', '.specimen-info .trash', function(e) {
        e.preventDefault();
        if (confirm('Are you sure you want to delete this specimen?')) {
            $(this).closest('.specimen-cont').remove();
        }
        return false;
    });

    $(".add-specimen").on('click', function () {  
        var specimencontent = '<div class="row form-row specimen-cont">' +
            '<div class="col-12 col-md-10 col-lg-11">' +
                '<div class="row form-row">' +
                    '<div class="col-12 col-md-6 col-lg-4">' +
                        '<div class="form-group">' +
                            '<label>Specimen Type</label>' +
                            '<select class="form-control" name="specimen_type">' +
                                '<option value="">Select Specimen Type</option>';
        // Populate specimen types dynamically from available specimen types
        for (var i = 0; i < specimenTypes.length; i++) {
            specimencontent += '<option value="' + specimenTypes[i] + '">' + specimenTypes[i] + '</option>';
        }
        specimencontent += '</select>' +
                        '</div>' +
                    '</div>' +
                    '<div class="col-12 col-md-6 col-lg-4">' +
                        '<div class="form-group">' +
                            '<极label>Collection Date</label>' +
                            '<input type="date" name="collection_date" class="form-control">' +
                        '</div>' +
                    '</div>' +
                    '<div class="col-12 col-md-6 col-lg-4">' +
                        '<div class="form-group">' +
                            '<label>Receiving Date</label>' +
                            '<div class="input-group">' +
                                '<input type="date" name="receiving_date" class="form-control">' +
                                '<div class="input-group-append">' +
                                    '<a href="#" class="btn btn-danger trash">' +
                                        '<i class="far fa-trash-alt"></i>' +
                                    '</a>' +
                                '</div>' +
                            '</div>' +
                        '</div>' +
                    '</div>' +
                '</div>' +
            '</div>' +
        '</div>';
        
        $(".specimen-info").append(specimencontent);
        return false;
    });
    
    // Form submission validation
    $(document).on('submit', 'form', function(e) {
        var isValid = true;
        
        // Validate specimen entry
        if (!validateSpecimenForm()) {
            isValid = false;
        }
        
        // Validate test results
        if (isValid && !validateTestResults极Form()) {
            isValid = false;
        }
        
        if (!isValid) {
            e.preventDefault();
        }
    });
})(jQuery);
