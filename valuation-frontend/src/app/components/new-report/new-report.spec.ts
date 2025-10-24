import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NewReport } from './new-report';

describe('NewReport', () => {
  let component: NewReport;
  let fixture: ComponentFixture<NewReport>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NewReport]
    })
    .compileComponents();

    fixture = TestBed.createComponent(NewReport);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
