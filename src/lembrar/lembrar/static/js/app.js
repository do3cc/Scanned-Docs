/*global alert: false, jQuery: false, window: false, Backbone: false, _: false, Mustache: false*/
(function (app, $, _, Backbone) {
    "use strict";
    var originalSync = Backbone.sync;
    Backbone.sxync = function (method, model, options) {
        if(options === undefined) {
            options = {};
        }
        if(options.dataType === undefined) {
            options.dataType = 'jsonp';
        }
        return originalSync(method, model, options);
    };
    app.init = function (base_url) {
        var routes = undefined,
            Doc = Backbone.Model.extend({}),
            DocsCollection = Backbone.Collection.extend({
                model: Doc,
                page: 0,
                filter_url: false,
                url: function () {
                    if(this.filter_url) {
                        this.filter_url = false;
                        if(this.getFilter()) {
                            return base_url + "/docs?filter=" + this.getFilter() + '&page=' + this.page;
                        } else {
                            return base_url + "/docs?page=" + this.page;
                        }
                    } else {
                        return base_url + '/docs';
                    }
                },
                getFilter: function () {
                    return this.filter_string || '';
                },
                setFilter: function (string) {
                    this.filter_string = string;
                    this.filter_url = true;
                    this.trigger("filterstring");
                    this.fetch();
                },
                nextPage: function () {
                    this.page += 1;
                    this.filter_url = true;
                    this.fetch();
                },
                prevPage: function () {
                    if(this.page) {
                        this.page -= 1;
                    }
                    this.filter_url = true;
                    this.fetch();
                },
                firstPage: function () {
                    this.page = 0;
                    this.filter_url = true;
                    this.fetch();
                },
                lastPage: function () {
                    this.page = -1;
                    this.filter_url = true;
                    this.fetch();
                }
            }),
            DocEditView = Backbone.View.extend({
                el: $("#nav-editview"),
                events: {
                    "click .save": "save",
                    "click .tag": "toggle_tag",
                    "click .new_tag_container .new_tag_action": "add_tag_init",
                    "keypress #new_tag": 'add_tag'
                },
                initialize: function () {
                    this.model.bind("change", this.render, this);
                },
                render: function () {
                    var $el = this.$el,
                        button_template = $el.find(".tags button.template"),
                        model = this.model;
                    $el.find(".tags button:not(.template)").remove();
                    $el.find("#new_tag").hide();
                    $el.find("#title-ro").text(this.model.get("title"));
                    $el.find("#title").val(this.model.get("title"));
                    $el.find("#description").val(this.model.get("description"));
                    $el.find("#tab1 img").attr('src', base_url + '/preview_doc/' + this.model.id);
                    $.getJSON(base_url + "/htmls_doc/" + this.model.id, function (data) {
                        var tab = $el.find("#tab2");
                        tab.empty();
                        _.each(data, function (elem) {
                            tab.append($("<div />").append(elem));
                        });
                        $el.removeClass("hide");
                    });
                    $.getJSON(base_url + "/stats/tags", function (tags) {

                        _.each(_.union(tags, model.get('tags')), function (tag) {
                            var button = button_template.clone();
                            button.removeClass('template hide');
                            button.text(tag);
                            if(!_.contains(model.get('tags'), tag)) {
                                button.addClass("disabled");
                            }
                            button.data("tagname", tag);
                            button_template.after(button);
                        });
                    });

                },
                toggle_tag: function (elem) {
                    var $elem = $(elem.target),
                        current_tags = this.model.get('tags'),
                        tag_change = $elem.data('tagname');
                    if(_.contains(current_tags, tag_change)) {
                        this.model.set({
                            tags: _.without(current_tags, tag_change)
                        });
                    } else {
                        this.model.set({
                            tags: _.union(current_tags, [tag_change])
                        });
                    }
                    return false;
                },
                add_tag: function (e) {
                    var model = this.model;
                    if(e.keyCode != 13){
                        return;
                    }
                    model.set({
                        tags: _.union(model.get('tags'), [e.target.value])
                    });
                    e.target.value = '';
                    $(e.target).hide();
                    return false;
                },
                add_tag_init: function(e){
                    $(e.target).parent().find("#new_tag").toggle();
                    return false;
                },
                hide: function () {
                    this.$el.addClass("hide");
                },
                save: function () {
                    var formdata = this.$el.find("form").serializeArray(),
                        modeldata = _.reduce(formdata, function (memo, elem) {
                            memo[elem.name] = elem.value;
                            return memo;
                        }, {});
                    this.model.set(modeldata);
                    this.model.save();
                    return false;
                }
            }),
            doceditview = undefined,
            DocView = Backbone.View.extend({
                tagName: 'tr',
                template: Mustache.compile($("#doc_template").html()),
                events: {
                    "click .delete": "delete_",
                    "click .edit": "edit",
                },
                initialize: function () {
                    _.bindAll(this.events);
                    this.model.bind("destroy", this.remove, this);
                },
                render: function () {
                    var params = this.model.toJSON(),
                        img = undefined;
                    params.preview_url = base_url + "/preview_doc/" + this.model.get('id');
                    params.img_url = base_url + "/binary_doc/" + this.model.get('id');

                    this.$el.html((this.template(params)));
                    img = this.$el.find('.preview');
                    img.attr('src', img.attr('imageurl'));
                    img = this.$el.find('.binary');
                    img.attr('href', img.attr('imageurl'));
                    return this;
                },
                delete_: function () {
                    this.model.destroy();
                },
                edit: function () {
                    doceditview = new DocEditView({
                        model: this.model
                    });
                    routes.navigate("edit/" + this.model.get("id"), {
                        trigger: true
                    });
                }
            }),
            DocsView = Backbone.View.extend({
                el: $("#docs_view"),
                events: {
                    "click .firstPage": "firstPage",
                    "click .lastPage": "lastPage",
                    "click .nextPage": "nextPage",
                    "click .prevPage": "prevPage"
                },
                initialize: function () {
                    this.model.bind("add", this.addOne, this);
                    this.model.bind("reset", this.reset, this);
                    this.$table = this.$el.find("table");
                },
                addOne: function (doc) {
                    var view = new DocView({
                        model: doc
                    });
                    this.$table.append(view.render().el);
                },
                reset: function () {
                    this.$table.empty();
                    this.model.each(this.addOne, this);
                },
                render: function () {
                    this.$el.parents('.container').removeClass("hide");
                },
                hide: function () {
                    this.$el.parents('.container').addClass("hide");
                },
                nextPage: function () {
                    this.model.nextPage();
                    return false;
                },
                prevPage: function () {
                    this.model.prevPage();
                    return false;
                },
                firstPage: function () {
                    this.model.firstPage();
                    return false;
                },
                lastPage: function () {
                    this.model.lastPage();
                    return false;
                }

            }),
            SearchView = Backbone.View.extend({
                el: $("#searchform"),
                events: {
                    "keydown form": "search"
                },
                initialize: function () {
                    this.model.bind("filterstring", this.render, this);
                    this.render();
                },
                render: function () {
                    this.$el.find("#search").val(this.model.getFilter());
                },
                search: function (event) {
                    if(event.keyCode === 13) {
                        this.model.setFilter(this.$el.find("#search").val());
                        return false;
                    }
                },
            }),
            docs = new DocsCollection(),
            docs_view = new DocsView({
                model: docs
            }),
            searchview = new SearchView({
                model: docs
            }),
            Routes = Backbone.Router.extend({
                routes: {
                    "": 'root',
                    "edit/:doc": 'edit'
                },
                initialize: function () {},
                hide_old: function () {
                    if(this.current_view) {
                        this.current_view.hide();
                    }
                },
                root: function () {
                    this.hide_old();
                    this.current_view = docs_view;
                    this.current_view.render();
                },
                edit: function (docid) {
                    this.hide_old();
                    if(doceditview === undefined) {
                        doceditview = new DocEditView({
                            model: docs.get(docid),
                            collection: docs
                        });
                    }
                    this.current_view = doceditview;
                    this.current_view.render();
                }
            }),
            routes = new Routes();
        docs.fetch({
            success: function () {
                Backbone.history.start()
            }
        });
        //routes.navigate("/");
        //docs_view.render();
    };

}(window.app = window.app || {}, jQuery, _, Backbone));