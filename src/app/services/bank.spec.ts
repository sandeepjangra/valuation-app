import { TestBed } from '@angular/core/testing';

import { Bank } from './bank';

describe('Bank', () => {
  let service: Bank;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Bank);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
