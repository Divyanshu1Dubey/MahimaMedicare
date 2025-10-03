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

    // Specimen Add More functionality
    $(".specimen-info").on('click','.trash', function () {
        $(this).closest('.specimen-cont').remove();
        return false;
    });

    $(".add-specimen").on('click', function () {  
        var specimencontent = '<div class="row form-row specimen-cont">' +
            '<div class="col-12 col-lg-12">' +
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
                            '<label>Collection Date</label>' +
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

    // Add Test functionality - same style as Add Specimen
    $(document).on('click', '.add-test', function () {
        var testHtml = '<div class="row form-row test-cont">' +
            '<div class="col-12 col-md-3">' +
                '<div class="form-group">' +
                    '<label>Test Name</label>' +
                    '<select class="form-control" name="test_name" required>' +
                        '<option value="">Select Test Name</option>';
        for (var i = 0; i < testNames.length; i++) {
            testHtml += '<option value="' + testNames[i].test_name + '">' + testNames[i].test_name + '</option>';
        }
        testHtml += '</select>' +
                '</div>' +
            '</div>' +
            '<div class="col-12 col-md-3">' +
                '<div class="form-group">' +
                    '<label>Result</label>' +
                    '<input type="text" name="result" class="form-control" required>' +
                '</div>' +
            '</div>' +
            '<div class="col-12 col-md-2">' +
                '<div class="form-group">' +
                    '<label>Unit</label>' +
                    '<input type="text" name="unit" class="form-control">' +
                '</div>' +
            '</div>' +
            '<div class="col-12 col-md-3">' +
                '<div class="form-group">' +
                    '<label>Referred Value</label>' +
                    '<input type="text" name="referred_value" class="form-control">' +
                '</div>' +
            '</div>' +
            '<div class="col-12 col-md-1">' +
                '<div class="form-group d-flex align-items-end" style="height: 100%;">' +
                    '<a href="#" class="btn btn-danger trash remove-test d-flex align-items-center justify-content-center" style="width: 100%;">' +
                        '<i class="far fa-trash-alt"></i>' +
                    '</a>' +
                '</div>' +
            '</div>' +
        '</div>';
        $(".test-info-container").append(testHtml);
        return false;
    });

    // Remove Test functionality
    $(".test-info-container").on('click', '.remove-test', function () {
        $(this).closest('.test-cont').remove();
        return false;
    });

    // Function to validate test form
    function validateTestForm() {
        var isValid = true;
        $('.test-cont').each(function() {
            var $testName = $(this).find('select[name="test_name"]');
            var $result = $(this).find('input[name="result"]');
            
            // Validate test name
            if (!$testName.val()) {
                alert('Please select a test name for all test entries.');
                $testName.focus();
                isValid = false;
                return false; // break out of each loop
            }
            
            // Validate result
            if (!$result.val()) {
                alert('Please enter a result for all test entries.');
                $result.focus();
                isValid = false;
                return false; // break out of each loop
            }
        });
        
        return isValid;
    }

    // Form submission validation
    $(document).on('submit', 'form', function(e) {
        var isValid = true;

        // Validate specimen entry
        if (!validateSpecimenForm()) {
            isValid = false;
        }

        // Validate test entry
        if (!validateTestForm()) {
            isValid = false;
        }

        if (!isValid) {
            e.preventDefault();
        }
    });
})(jQuery);
