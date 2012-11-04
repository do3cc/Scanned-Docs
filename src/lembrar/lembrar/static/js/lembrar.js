/*global alert: false, jQuery: false, window: false */
(function (lembrar, $) {
    "use strict";
    lembrar.init = function (base_url, error_handler) {
        var retval = {};
        if (error_handler === undefined) {
            error_handler = function (error) {
                alert(error);
            };
        }
        retval.error_handler = error_handler;
        retval.get = function (callable, skip) {
            if (skip === undefined) {
                skip = 0;
            }
            $.ajax({
                url: base_url + '/docs?skip=' + skip + '&callback=' + callable,
                error: retval.error_handler,
                dataType: 'jsonp'
            });
        };
        return retval;
    };

}(window.lembrar = window.lembrar || {}, jQuery));

// if(document.lembrar === undefined){
//     lembrar = {};
// }
// lembrar.edit_init = function(){
//     var modal_image = $("#modal-image");
//     modal_image.click(function(){
//         $(this).modal('toggle');
//     });
//     var keyword_field = $("textarea[name='keywords']");
//     var keyword_buttons = $(".keywords > li > a");
//     function updateButtons(){
//         keyword_buttons.each(function(){
//             var $this = $(this);
//             if(keyword_field.val().indexOf($this.text()) == -1){
//                 $this.toggleClass("disabled");
//             }
//         });
//     };
//     function toggleKeyword(){
//         var $this = $(this);
//         if($this.is(".disabled")){
//             keyword_field.val(keyword_field.val() + "\n" + $this.text());
//         }else{
//             keyword_field.val(keyword_field.val().replace($this.text(), ""));
//         }
//         keyword_field.val(keyword_field.val().trim());
//         updateButtons();
//     };
//     updateButtons();
//     keyword_field.change(updateButtons);
//     keyword_buttons.click(toggleKeyword);
//     var searchterms = $("#searchterms");
//     searchterms.hide();
//     $("#searchterms_header").click(function(){
//         searchterms.toggle();
//     })
// };
// lembrar.base_init = function(){
//     $(".temporary_notifications > div").alert();
// }