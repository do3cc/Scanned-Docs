if(document.scanned_docs === undefined){
    scanned_docs = {};
}

scanned_docs.edit_init = function(){
    var modal_image = $("#modal-image");
    modal_image.click(function(){
        $(this).modal('toggle');
    });
    var keyword_field = $("textarea[name='keywords']");
    var keyword_buttons = $(".keywords > li > a");
    function updateButtons(){
        keyword_buttons.each(function(){
            var $this = $(this);
            if(keyword_field.val().indexOf($this.text()) == -1){
                $this.toggleClass("disabled");
            }
        });
    };
    function toggleKeyword(){
        var $this = $(this);
        if($this.is(".disabled")){
            keyword_field.val(keyword_field.val() + "\n" + $this.text());
        }else{
            keyword_field.val(keyword_field.val().replace($this.text(), ""));
        }
        keyword_field.val(keyword_field.val().trim());
        updateButtons();
    };
    updateButtons();
    keyword_field.change(updateButtons);
    keyword_buttons.click(toggleKeyword);

    var searchterms = $("#searchterms");
    searchterms.hide();
    $("#searchterms_header").click(function(){
        searchterms.toggle();
    })
};

scanned_docs.base_init = function(){
    $(".temporary_notifications > div").alert();
}

