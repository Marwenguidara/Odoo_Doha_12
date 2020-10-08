odoo.define('hr_dashboard.dashboard', function (require) {
"use strict";
var core = require('web.core');
var framework = require('web.framework');
var session = require('web.session');
var ajax = require('web.ajax');
var ActionManager = require('web.ActionManager');
var view_registry = require('web.view_registry');
var Widget = require('web.Widget');
var AbstractAction = require('web.AbstractAction');
var ControlPanelMixin = require('web.ControlPanelMixin');
var QWeb = core.qweb;

var _t = core._t;
var _lt = core._lt;

var HrDashboardView = AbstractAction.extend(ControlPanelMixin, {
	events: {
        'click .my_profile': 'action_my_profile',
        //'click .line_click': 'line_click',

	},
	init: function(parent, context) {
        this._super(parent, context);
        var employee_data = [];
        var self = this;
        if (context.tag == 'hr_dashboard.dashboard') {
            self._rpc({
                model: 'hr.dashboard',
                method: 'get_employee_info',
            }, []).then(function(result){
                self.employee_data = result[0]
                console.log(self.employee_data)
            }).done(function(){
                self.render();
                self.href = window.location.href;
            });

        }

    },
    willStart: function() {
         return $.when(ajax.loadLibs(this), this._super());
    },
    start: function() {
        var self = this;
        return this._super();
    },
    render: function() {
        var super_render = this._super;
        var self = this;
        var hr_dashboard = QWeb.render('hr_dashboard.dashboard',{ widget: this });
        $( ".o_control_panel" ).addClass( "o_hidden" );
        $(hr_dashboard).prependTo(self.$el);

        $('#project').select2({
            maximumSelectionSize: 1
        });
        $('#drawing').select2({
            maximumSelectionSize: 1
        });
        $('#project').on( 'change', function () {
        $('#emp_details').DataTable().column(0).search( this.value ).draw();
        } );
        $('#drawing').on( 'change', function () {
        $('#emp_details').DataTable().column(1).search( this.value ).draw();
        } );

        self.previewTable();
        self.previewTableProgress();
        return hr_dashboard
    },
    reload: function () {
            window.location.href = this.href;
    },


    action_my_profile: function(event) {
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("My Profile"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            res_id: self.employee_data.id,
            view_mode: 'form',
            view_type: 'form',
            views: [[false, 'form']],
            context: {'edit': true},
            domain: [],
            target: 'inline'
        },{on_reverse_breadcrumb: function(){ return self.reload();}})
    },
    // Function which gives random color for charts.
    getRandomColor: function () {
        var letters = '0123456789ABCDEF'.split('');
        var color = '#';
        for (var i = 0; i < 6; i++ ) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    },
        // line_click: function (e) {
        //     var self = this;
        //     var tr = $(this).closest('tr');
        //      var row = table.row( tr );

        //     var line = row.data();
        //     console.log(line)
        //     // based on this line_type, we will decide that we are clicked on journal items or not
        //     //for (var j in self.employee_data.emp_table.){
        //     //        if(self.journal_items[j]['id'] == line){
        //     //            self.do_action({
        //      //               type: 'ir.actions.act_window',
        //      //               res_model: "account.move",
        //      //               res_id: self.journal_items[j]['j_id'],
        //      //               views: [[false, 'form']],
        //      //           });
        //      //       }
        //     //}


        //     return;
        // },



    previewTable: function() {
        var self = this;
        var collapsedGroups = {};
        var table = $('#emp_details').DataTable( {
        order: [[0, 'asc']],
        rowGroup: {
        // Uses the 'row group' plugin
        dataSrc: [ 0],

        startRender: function (rows, group) {

            var intVal = function ( i ) {
                return typeof i === 'string' ?
                    i.replace(/[<span></span>]/g, '')*1:
                    typeof i === 'number' ?
                        i : 0;
            };

            var collapsed = !!collapsedGroups[group];
            rows.nodes().each(function (r) {
                r.style.display = collapsed ? 'none' : '';
            });

             // var nb_reel = rows
             //        .data()
             //        .pluck(5)
             //        .reduce( function (a, b) {
             //            return a + b.replace(/[^\d]/g, '')*1;
             //        },0);
             var total_drwing = rows
                    .data()
                    .pluck(6)
                    .reduce( function (a, b) {
                        console.log(intVal(a))
                        console.log(intVal(b))
                        var som = intVal(a) + intVal(b)
                        return som.toFixed(2);
                    },0)
            var total_derivly = rows
                    .data()
                    .pluck(4)
                    .reduce( function (a, b) {
                        console.log(intVal(a))
                        console.log(intVal(b))
                        var som = intVal(a) + intVal(b)
                        return som.toFixed(2);
                    },0)
            var total_prod = rows
                    .data()
                    .pluck(3)
                    .reduce( function (a, b) {
                        console.log(intVal(a))
                        console.log(intVal(b))

                        var som = intVal(a) + intVal(b)
                        return som.toFixed(2);
                    },0)
            var total_erec = rows
                    .data()
                    .pluck(5)
                    .reduce( function (a, b) {
                        console.log(intVal(a))
                        console.log(intVal(b))
                        var som = intVal(a) + intVal(b)
                        return som.toFixed(2);
                    },0)

            // Add category name to the <tr>. NOTE: Hardcoded colspan
            return $('<tr/>')
                .append('<td>' + group + ' (' + rows.count() + ')</td><td><td style="text-align:center;">' + total_prod + '</td><td style="text-align:center;">' + total_derivly + '</td><td style="text-align:center;">' + total_erec + '</td><td style="text-align:center;">' + total_drwing + '</td>')
                .attr('data-name', group)
                .toggleClass('collapsed', collapsed);
        }

        },
            dom: 'Bfrtip',
            buttons: [
                'excel',
                {
                    extend: 'pdf',
                    footer: 'true',
                    orientation: 'landscape',
                    title:'Dashboard Details',
                    text: 'PDF',
                    exportOptions: {
                        modifier: {
                            selected: true
                        }
                    }
                },

            ],
            columnDefs: [ {
            targets:0 ,
            visible: false
        } ],
        "scrollY": "400px",
        "paging": false,

        } );
        $('#emp_details tbody').on('click','tr.dtrg-start',function () {
        console.log('tttttttttttttpssssssssssi')
        console.log(self.employee_data)
        var name = $(this).data('name');
        collapsedGroups[name] = !collapsedGroups[name];
        table.draw(false);
    });
        $('#emp_details tbody').on('click', '.line_click', function () {

        var tr = $(this).closest('tr');
        var row = table.row( tr );
        var line = row.data(self.employee_data.emp_table.codes)[7];
        var l = line.split('<span>').pop().split('</span>')[0];
        var id = parseInt(l);

         console.log(id)
         self.do_action({
                            type: 'ir.actions.act_window',
                            res_model: "construction.drawing",
                            res_id: id,
                            views: [[false, 'form']],
                        },{on_reverse_breadcrumb: function(){ return self.reload();}});
    });

    },
 previewTableProgress: function() {
        var self = this;
        var collapsedGroups = {};
        var table = $('#progress_details').DataTable( {
        order: [[0, 'asc']],
        rowGroup: {
        // Uses the 'row group' plugin
        dataSrc: [ 0],

        startRender: function (rows, group) {

            var intVal = function ( i ) {
                return typeof i === 'string' ?
                    i.replace(/[<span></span>]/g, '')*1:
                    typeof i === 'number' ?
                        i : 0;
            };

            var collapsed = !!collapsedGroups[group];
            rows.nodes().each(function (r) {
                r.style.display = collapsed ? 'none' : '';
            });

             var nb_item = rows
                    .data()
                    .pluck(2)
                    .reduce( function (a, b) {
                       return a + b.replace(/[^\d]/g, '')*1;
                    },0);

             
             var prog_total = rows
                    .data()
                    .pluck(6)
                    .reduce( function (a, b) {
                       return a + b.replace(/[^\d]/g, '')*1;
                    },0)/rows.count();
            var prog_derivly = rows
                    .data()
                    .pluck(4)
                    .reduce( function (a, b) {
                        return a + b.replace(/[^\d]/g, '')*1;
                    },0)/rows.count();
            var prog_prod = rows
                    .data()
                    .pluck(3)
                    .reduce( function (a, b) {
                        console.log(rows.count())

                        return a + b.replace(/[^\d]/g, '')*1;
                    },0)/rows.count();
            var prog_erec = rows
                    .data()
                    .pluck(5)
                    .reduce( function (a, b) {
                        return a + b.replace(/[^\d]/g, '')*1;
                    },0)/rows.count();

            // Add category name to the <tr>. NOTE: Hardcoded colspan
            return $('<tr/>')
                .append('<td>' + group + ' (' + rows.count() + ')<td style="text-align:center;">'+nb_item+'</td><td style="text-align:center;">'+prog_prod.toFixed(0)+'%</td><td style="text-align:center;">'+prog_derivly.toFixed(0)+' %</td><td style="text-align:center;">'+prog_erec.toFixed(0)+' %</td><td style="text-align:center;">'+prog_total.toFixed(0)+' %</td>')
                .attr('data-name', group)
                .toggleClass('collapsed', collapsed);
        }

        },
            dom: 'Bfrtip',
            buttons: [
                'excel',
                {
                    extend: 'pdf',
                    footer: 'true',
                    orientation: 'landscape',
                    title:'Dashboard Details',
                    text: 'PDF',
                    exportOptions: {
                        modifier: {
                            selected: true
                        }
                    }
                },

            ],
            columnDefs: [ {
            targets:0 ,
            visible: false
        } ],
        "scrollY": "400px",
        "paging": false,

        } );
        $('#progress_details tbody').on('click','tr.dtrg-start',function () {
        console.log('tttttttttttttpssssssssssi')
        console.log(self.employee_data)
        var name = $(this).data('name');
        collapsedGroups[name] = !collapsedGroups[name];
        table.draw(false);
    });
        $('#progress_details tbody').on('click', '.line_click', function () {

        var tr = $(this).closest('tr');
        var row = table.row( tr );
        var line = row.data(self.employee_data.emp_table.codes)[7];
        var l = line.split('<span>').pop().split('</span>')[0];
        var id = parseInt(l);

         console.log(id)
         self.do_action({
                            name: 'Item_number',
                            type: 'ir.actions.act_window',
                            res_model: "item.number",
                            view_mode: 'kanban,tree,form',
                            views: [[false, 'kanban'],[false, 'list'],[false, 'form']],
                            context: "{'drawing_id': %d}" % (id),
                            domain: [['drawing_id','=',id]],
                        },{on_reverse_breadcrumb: function(){ return self.reload();}});
    });

    },

});

core.action_registry.add('hr_dashboard.dashboard', HrDashboardView);
return HrDashboardView
});
