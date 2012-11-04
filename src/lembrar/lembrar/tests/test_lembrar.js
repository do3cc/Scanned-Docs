/*global test: false, lembrar: false, ok: false, equals: false */
(function () {
    'use strict';
    test("lembrar init", function () {
        var test_ob = lembrar.init('test', 'error_handler');
        ok('error_handler' === test_ob.error_handler);
    });

    test("lembrar get", function () {
        var test_ob = lembrar.init('test'),
            test_data = 'test';

        $.ajax = function(options){
            equal(options.url, 'test/docs?skip=0&callback=test2');
        }
        test_ob.get('test2');
    });

    test("lembrar get2", function(){
        var test_ob = lembrar.init('test');

        $.ajax = function(options){
            equal(options.url, 'test/docs?skip=30&callback=test2');
        }
        test_ob.get('test2', 30);
    })
}());