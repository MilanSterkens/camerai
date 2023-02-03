import { TestBed } from '@angular/core/testing';

import { CameraiService } from './camerai.service';

describe('CameraiService', () => {
  let service: CameraiService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CameraiService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
