import { createApp } from 'vue';
import App from './App.vue';
import NHSActionLink from './components/NHSActionLink.vue';
import NHSBackLink from './components/NHSBackLink.vue';
import NHSButton from './components/NHSButton.vue';
import NHSCard from './components/NHSCard.vue';
import NHSCardGroup from './components/NHSCardGroup.vue';
import NHSCardGroupItem from './components/NHSCardGroupItem.vue';
import NHSCheckboxes from './components/NHSCheckboxes.vue';
import NHSCheckboxItem from './components/NHSCheckbox.vue';
import NHSDetails from './components/NHSDetails.vue';
import NHSErrorMessage from './components/NHSErrorMessage.vue';
import NHSErrorSummary from './components/NHSErrorSummary.vue';
import NHSExpander from './components/NHSExpander.vue';
import NHSFieldset from './components/NHSFieldset.vue';
import NHSFormGroup from './components/NHSFormGroup.vue';
import NHSGridRow from './components/NHSGridRow.vue';
import NHSGridItem from './components/NHSGridItem.vue';
import NHSHeader from './components/NHSHeader.vue';
import NHSHeading from './components/NHSHeading.vue';
import NHSHint from './components/NHSHint.vue';
import NHSInsetText from './components/NHSInsetText.vue';
import NHSLabel from './components/NHSLabel.vue';
import NHSMain from './components/NHSMain.vue';
import NHSSelect from './components/NHSSelect.vue';
import NHSSummaryList from './components/NHSSummaryList.vue';
import NHSSummaryListRow from './components/NHSSummaryListRow.vue';
import NHSTable from './components/NHSTable.vue';
import NHSTag from './components/NHSTag.vue';
import NHSTextInput from './components/NHSTextInput.vue';
import NHSWarningCallout from './components/NHSWarningCallout.vue';

import router from './router';

createApp(App)
  .component(NHSActionLink.name, NHSActionLink)
  .component(NHSBackLink.name, NHSBackLink)
  .component(NHSButton.name, NHSButton)
  .component(NHSCard.name, NHSCard)
  .component(NHSCardGroup.name, NHSCardGroup)
  .component(NHSCardGroupItem.name, NHSCardGroupItem)
  .component(NHSCheckboxes.name, NHSCheckboxes)
  .component(NHSCheckboxItem.name, NHSCheckboxItem)
  .component(NHSDetails.name, NHSDetails)
  .component(NHSErrorMessage.name, NHSErrorMessage)
  .component(NHSErrorSummary.name, NHSErrorSummary)
  .component(NHSExpander.name, NHSExpander)
  .component(NHSFieldset.name, NHSFieldset)
  .component(NHSFormGroup.name, NHSFormGroup)
  .component(NHSGridRow.name, NHSGridRow)
  .component(NHSGridItem.name, NHSGridItem)
  .component(NHSHeader.name, NHSHeader)
  .component(NHSHeading.name, NHSHeading)
  .component(NHSHint.name, NHSHint)
  .component(NHSInsetText.name, NHSInsetText)
  .component(NHSLabel.name, NHSLabel)
  .component(NHSMain.name, NHSMain)
  .component(NHSSelect.name, NHSSelect)
  .component(NHSSummaryList.name, NHSSummaryList)
  .component(NHSSummaryListRow.name, NHSSummaryListRow)
  .component(NHSTable.name, NHSTable)
  .component(NHSTag.name, NHSTag)
  .component(NHSTextInput.name, NHSTextInput)
  .component(NHSWarningCallout.name, NHSWarningCallout)
  .use(router)
  .mount('#app');
