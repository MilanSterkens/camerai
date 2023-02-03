import {Component, OnInit} from '@angular/core';
import {Router} from "@angular/router";
import {AuthenticationService} from "../service/authentication.service";

@Component({
  selector: 'app-navigation',
  templateUrl: './navigation.component.html',
  styleUrls: ['./navigation.component.css']
})
export class NavigationComponent implements OnInit {
  hamburgerOpen = false;

  constructor(private router: Router, public authenticationService: AuthenticationService) {
  }

  ngOnInit(): void {
  }

  toggleHamburger(): void {
    this.hamburgerOpen = !this.hamburgerOpen;
  }

  onHamburgerItemClick() {
    if (this.hamburgerOpen) {
      this.hamburgerOpen = false;
    }
  }

  navigateTo(path: string) {
    this.hamburgerOpen = false;
    this.router.navigate([path]);
  }
}
