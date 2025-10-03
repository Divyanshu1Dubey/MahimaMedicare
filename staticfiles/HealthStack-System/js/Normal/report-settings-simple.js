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
        '极Throat Swab',
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
            var $collectionDate = $(this).find('极input[name="collection_date"]');
            var $receivingDate = $(this).find('input[name="receiving_date"]');
            
            // Validate specimen type
            if (!$specimenType.val()) {
                alert('Please select a specimen type for all specimen entries.');
                $specimen极Type.focus();
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
                            '<label>Collection Date</label>' +
                            '<input type="date" name="collection_date"极 class="form-control">' +
                        '</div>' +
                    '</div>' +
                    '<div class="col-12 col-md-6 col-lg-4">' +
                        '<div class="form-group">' +
                            '<label>Receiving Date</label>' +
                            '<input type="date" name="receiving_date" class="form-control">' +
                        '</div>' +
                    '</极div>' +
                '</div>' +
            '</div>' +
            '<div class="col-12 col-md-2 col-lg-1"><label class="d-md-block d-sm-none d-none">&nbsp;</label><a href="#" class="btn btn-danger trash"><i class="far fa-trash-alt"></i></a></div>' +
        '</div>';
        
        $(".specimen-info").append(specimencontent);
        return false;
    });
    
    // Test Add More functionality
    $(document).on('click', '.test-info .trash', function(e) {
        e.preventDefault();
        if (confirm('Are you sure you want to delete this test?')) {
            $(this).closest('.test-cont').remove();
        }
        return false;
    });

    $(".add-test").on('click', function () {  
        // Clone the first test-cont div
        var $firstTest = $(".test-info-container .test-cont").first();
        if ($firstTest.length === 0) {
            // If no test-cont exists, create one manually (fallback)
            var testcontent = '<div class="row form-row test-cont" style="margin-bottom: 15px;">' +
                '<div class="col-12 col-md-2">' +
                    '<div class="form-group">' +
                        '<label>Test Name</label>' +
                        '<select class="form-control test-list-select" name="test_name[]" required>' +
                            '<option value="">Select Test Name</option>';
            
            for (var i = 0; i < testNames.length; i++) {
                testcontent += '<option value="' + testNames[i].test_name + '" data-test-id="' + testNames[i].test_id + '">' + 
                               testNames[i].test_name + '</option>';
            }
            
            testcontent += '</select>' +
                        '</div>' +
                    '</div>' +
                    '<div class="col-12 col-md-2">' +
                        '<div class="form-group">' +
                            '<label>Result</label>' +
                            '<input type="text" name="result[]" class="form-control" required>' +
                        '</div>' +
                    '</div>' +
                    '<div class="col-12 col-md-2">' +
                        '<div class="form-group">' +
                            '<label>Unit</label>' +
                            '<input type="text" name="unit[]" class="form-control">' +
                        '</div>' +
                    '</div>' +
                    '<div class="col-12 col-md-2">' +
                        '<div class="form-group">' +
                            '<label>Referred Value</label>' +
                            '<input type="text" name="referred_value[]" class="form-control">' +
                        '</div>' +
                    '</div>' +
                    '<div class="col-12 col-md-2">' +
                        '<div class="form-group">' +
                            '<label class="d-md-block d-sm-none d-none">&nbsp;</label>' +
                            '<a href="#" class="btn btn-danger trash">' +
                                '<i class="far fa-trash-alt"></i> Delete' +
                            '</a>' +
                        '</div>' +
                    '</div>' +
                '</div>';
            
            $(".test-info-container").append(testcontent);
        } else {
            // Clone and reset values
            var $clone = $firstTest.clone();
            $clone.find('select[name="test_name[]"]').val('');
            $clone.find('input[name="result[]"]').val('');
            $clone.find('input[name="unit[]"]').val('');
            $clone.find('input[name="referred_value[]"]').val('');
            $(".test-info-container").append($clone);
        }
        return false;
    });

    // Function to validate test form
    function validateTestForm() {
        var isValid = true;
        $('.test-cont').each(function() {
            var $testName = $(this).find('select[name="test_name[]"]');
            var $result = $(this).find('input[name="result[]"]');
            
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
