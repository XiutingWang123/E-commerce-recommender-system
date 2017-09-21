<form action="/recommend" method="post">
Enter source items: <input name="keywords" type="text" />
<input type="submit" /><br/>
</form>

<p>You clicked these items: {{keyword}}</p>

<p>You may also like (from popularity model): </p>

<table border="0">
   %for item in recommend_list[0]:
     <tr>
       <td>Item ID: {{item}}</td>
     </tr>
   %end
</table>

<p>You may also like (from item kNN model): </p>

<table border="0">
   %for item in recommend_list[1]:
     <tr>
       <td>Item ID: {{item}}</td>
     </tr>
   %end
</table>