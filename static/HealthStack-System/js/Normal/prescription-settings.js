/*
Author       : Dreamguys
Template Name: Doccure - Bootstrap Template
Version      : 1.0
*/

(function($) {
    "use strict";

    // medicine Add More
    
    $(".medicine-info").on('click','.trash', function () {
        $(this).closest('.medicine-cont').remove();
        return false;
    });

    $(".add-medicine").on('click', function () {  
        
        var medicinecontent = '<div class="row form-row medicine-cont">' +
            '<div class="col-12 col-md-10 col-lg-11">' +
                '<div class="极row form-row">' +
                    '<div class="col-12 col-md-6 col-lg-3">' +
                        '<div class="form-group">' +
                            '<label>Medicine Name</label>' +
                            '<input type="text" name="medicine_name" class="form-control">' +
                        '</div>' +
                    '</div>' +
                    '<div class="col-12 col-md-6 col-lg-3">' +
                        '<div class="form-group">' +
                            '<label>Quantity</label>' +
                            '<input type="text" name="quantity" class="form-control">' +
                        '</div>' +
                    '</div>' +
                    '<div class="col-12 col-md-6 col-lg-3">' +
                        '<div class="form-group">' +
                            '<label>Frequency</label>' +
                            '<input type="text" name="frequency" class="form-control">' +
                        '</div>' +
                    '</div>' +
                    '<div class="col-12 col-md-6 col-lg-3">' +
                        '<div class="form-group">' +
                            '<label>Relation with meal</label>' +
                            '<input type="text" name="relation_with_meal" class="form-control">' +
                        '</div>' +
                    '</div>' +
                    '<div class="col-12 col-md-6 col-lg-6">' +
                        '<div class="form-group">' +
                            '<label>Duration</label>' +
                            '<input type="text" name="duration" class="form-control">' +
                        '</div>' +
                    '</div>' +
                    '<div class="col-12 col-md-6 col-lg-6">' +
                        '<div class="form-group">' +
                            '<label>Instruction</label>' +
                            '<input type="text" name="instruction" class="form-control">' +
                        '</div>' +
                    '</div>' +
                '</div>' +
            '</div>' +
            '<div class="col-12 col-md-2 col-lg-1"><label class="d-md-block d-sm-none d-none">&nbsp;</label><a href="#" class="btn btn-danger trash"><i class="far fa-trash-alt"></极i></a></div>' +
        '</div>';
        
        $(".medicine-info").append(medicinecontent);
        return false;
    });    
    
    
    // Test Add More

    $(".test-info").on('click','.trash', function () {
        $(this).closest('.test-cont').remove();
        return false;
    });

    $(".add-test").on('click', function () {  
        
        // Generate test options directly from testData
        var testOptions = '<option value="">Select Test</option>';
        if (typeof testData !== 'undefined' && testData.length > 0) {
            testData.forEach(function(test) {
                testOptions += '<option value="' + test.test_id + '" data-test-id="' + test.test_id + '">' + test.test_name + '</option>';
            });
        }
        
        var testcontent = '<div class="row form-row test-cont">' +
            '<div class="col-12 col-md-10 col-lg-11">' +
                '<div class="row form-row">' +
                    '<div class="col-12 col-md-5 col-lg-5">' +
                        '<div class="form-group">' +
                            '<label>Test Name</label>' +
                            '<select class="form-control test-name-select" name="test_name" onchange="updateTestId(this)">' +
                                testOptions +
                            '</select>' +
                        '</div>' +
                    '</div>' +
                    '<div class="col-12 col-md-6 col-lg-6">' +
                        '<div class="form-group">' +
                            '<label>Description</label>' +
                            '<input type="text" name="description" class="form-control">' +
                        '</div>' +
                    '</div>' +
                    '<div class="col-12 col-md-1 col-lg-1">' +
                        '<div class="form-group">' +
                            '<label>ID</label>' +
                            '<input type="number" name="id" class="form-control test-id-input" readonly>' +
                        '</div>' +
                    '</div>' +
                    
                '</div>' +
            '</div>' +
            '<div class="col-12 col-md-2 col-lg-1"><label class="d-md-block d-sm-none d-none">&nbsp;</label><a href="#" class="btn btn-danger trash"><i class="far fa-trash-alt"></i></a></div>' +
        '</div>';
        
        $(".test-info").append(testcontent);
        return false;
    });

        
})(jQuery);
