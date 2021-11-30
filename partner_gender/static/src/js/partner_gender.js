odoo.define('partner_gender.gender',function(require) {
    'use strict';

    $('document').ready(function (event) {
        let gender = $('select[name=gender] option').filter(':selected').val()
        if (gender !== 'other') {
            $('#gender_txt').attr('style', 'display:none !important;')
            $("#gender_txt_input").prop('required', false);
        } else {
            $('#gender_txt').attr('style', 'display:unset !important;' )
            $("#gender_txt_input").prop('required', true);
        }

        $( '#gender' ).unbind().change(function () {
            gender = $('select[name=gender] option').filter(':selected').val()
            if (gender !== 'other') {
                $('#gender_txt').attr('style', 'display:none !important;')
                $("#gender_txt_input").prop('required', false);
            } else {
                $('#gender_txt').attr('style', 'display:unset !important;' )
                $("#gender_txt_input").prop('required', true);
            }
        })
    })
})

