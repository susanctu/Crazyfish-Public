var CfUtils = {
		format_as_day_month_date: function (dateObj) {
			var weekday=new Array(7);
			weekday[0]="Sun";
			weekday[1]="Mon";
			weekday[2]="Tue";
			weekday[3]="Wed";
			weekday[4]="Thu";
			weekday[5]="Fri";
			weekday[6]="Sat";
			var day = weekday[dateObj.getDay()];
			var monthNames=new Array(12);
			monthNames[0]="Jan";
			monthNames[1]="Feb";
			monthNames[2]="Mar";
			monthNames[3]="Apr";
			monthNames[4]="May";
			monthNames[5]="Jun";
			monthNames[6]="Jul";
			monthNames[7]="Aug";
			monthNames[8]="Sept";
			monthNames[9]="Oct";
			monthNames[10]="Nov";
			monthNames[11]="Dec";
			var month = monthNames[dateObj.getMonth()];               
			var date = dateObj.getDate();
			var year = dateObj.getFullYear();
			if(date < 10) 
				date = "0" + date;
			return day + ' ' + month + ' ' + date + ' ' + year;
		}
}
