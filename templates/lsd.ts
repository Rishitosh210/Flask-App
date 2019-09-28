
import { Component } from '@angular/core';
import {Http, Response} from '@angular/http';
import {Observable} from 'rxjs';
import 'rxjs/add/operator/map';
 
 
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
 
  constructor(private _http:Http) {
    this.c1.name = "eli"
   }
  title = 'app';
  imgsrc='';
  pandas='';
  imgsbsrc='';
  str1='';
  resavg='';
  getimage(){
  	this.imgsrc = '/getimg';
  }
  c1:Cust = new Cust();
  click1(){
    this.getAllBooks().subscribe(b => this.c1 = b)
 
  }
  getavg(){
  	this._http.get("/getavg?val=" + this.str1).map(r=>r.text()).subscribe(res => this.resavg= res)
  }
  getDF(){
    this._http.get("./getdata").map(r => r.text()).subscribe(v => this.pandas = v);  
  }
  getAllBooks()
  {
    return this._http
          .get("./getcust")
          .map(r => <Cust>r.json())
 
  }
  getsbimage()
  {
  	this.imgsbsrc = '/getsbdata';
  }
}
 
export class Cust{
    name:string;
    age:number;
    city:string;
}