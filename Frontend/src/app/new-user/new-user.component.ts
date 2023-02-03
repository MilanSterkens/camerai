import { Component, OnInit } from '@angular/core';
import {Router} from "@angular/router";
import {CameraiService} from "../service/camerai.service";

@Component({
  selector: 'app-new-user',
  templateUrl: './new-user.component.html',
  styleUrls: ['./new-user.component.css']
})
export class NewUserComponent implements OnInit {

  constructor(private router: Router, private service: CameraiService) { }

  ngOnInit(): void {
  }

  goBack (){
    this.router.navigate(['users']);
  }

  addUser(email: string) {
    const user: any = {
      email: email
    };
    this.service.postUser(user).subscribe((any) => {
    });
    this.router.navigate(["users"]);
  }
}
