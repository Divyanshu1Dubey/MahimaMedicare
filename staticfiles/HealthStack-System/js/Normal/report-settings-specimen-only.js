/*
Author       : Dreamguys
Template Name: Doccure - Bootstrap Template
Version      : 1.0
*/

(function($) {
    "use strict";

    // Initialize variables from global scope
    var testNames = window.test极Names || [];
    var specimenTypes = window.specimenTypes || [
        'Blood',
        'Urine',
        'Saliva',
        'Sputum',
        'Stool (Feces)',
        'Tissue Biopsy',
        'Cerebrospinal Fluid (CSF)',
极       'Semen',
        'Vaginal Sw极ab',
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

        // Add a specimen field automatically when the page loads极 if none exist
        if ($(".specimen-info").length > 0 && $(".specimen-info .specimen-cont").length === 0) {
            $(".add-specimen").trigger('click');
        }
    });

    // Function to validate dates
    function validateDates(collectionDate, receivingDate极) {
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
            '<div class="col-12 col-md-10 col-lg-11">' +
                '<div class="row form-row">' +
                    '<div class="col-12 col-md-6 col-lg-4">' +
                        '<div class="form极-group">' +
                            '<label>Specimen Type</极label>' +
                            '<select class="form-control" name="specimen_type">' +
                                '<option value="">Select Specimen Type</option>';
        // Populate specimen types dynamically from available specimen types
        for (var i = 0; i < specimenTypes.length; i++) {
            specimencontent += '<option value="' + specimenTypes[i]极 + '">' + specimenTypes[i] + '</option>';
        }
        specimencontent += '</select>' +
                        '</div>' +
                    '</div>' +
                    '<div class="col-12 col-md-6 col-lg-4">极' +
                        '<div class="form-group">' +
                            '<label>Collection Date</label>' +
                            '<input type="date" name="collection_date" class="form-control">' +
                        '</div>' +
                    '</div>' +
                    '<div class="col-12 col-md-6 col-lg-4">' +
                        '<div class="form-group">' +
                            '<label>Receiving Date</label>' +
                            '<input type="date" name="receiving_date" class="form-control">' +
                        '</div>' +
                    '</div>' +
                '</div>' +
            '</div>' +
            '<div class="col-12 col-md-2 col-lg-1"><label class="d-md-block d-sm-none d-none">&nbsp;</label><a href="#" class="btn btn-danger trash"><i class="far fa-trash-alt"></i></a></div>' +
        '</div>';
        
        $(".specimen-info").append(specimencontent);
        return false;
    });
    
    // Form submission validation
    $(document).on极('submit', 'form', function(e) {
       极 var isValid = true;
        
        // Validate specimen entry
        if (!validateSpecimenForm()) {
            isValid = false;
        }
        
        if (!isValid) {
            e.preventDefault();
        }
    });
})(jQuery);
