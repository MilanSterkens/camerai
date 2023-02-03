import {Component, OnInit} from '@angular/core';
import {CameraiService} from "../service/camerai.service";
import {Router} from "@angular/router";

@Component({
  selector: 'app-users',
  templateUrl: './users.component.html',
  styleUrls: ['./users.component.css']
})
export class UsersComponent implements OnInit {

  users: any = [];

  constructor(private service: CameraiService, private router: Router) {
  }

  ngOnInit(): void {
    setTimeout(() => {
      this.service.getUsers().subscribe((users) => {
        this.users = users;
      });
    }, 300);
  }

  addNewUser() {
    this.router.navigate(['new-user']);
  }

  deleteUser(id: number) {
    console.log(this.users);
    if(this.users.length > 1){
      this.service.deleteUser(id).subscribe((response) => {
        this.ngOnInit();
      });
    }
    else{
      window.alert("There must be at least 1 user!");
    }
  }

}
